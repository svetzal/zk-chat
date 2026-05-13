"""
Document Service for Zettelkasten

This service provides functionality for document lifecycle operations in a Zettelkasten.
It handles document CRUD operations without indexing concerns, delegating file system
operations to the MarkdownFilesystemGateway.
"""

from collections.abc import Iterator

import structlog
import yaml

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument

logger = structlog.get_logger()


class DocumentService:
    """
    Service for managing document lifecycle operations in a Zettelkasten.

    Handles document CRUD operations including:
    - Reading and writing documents
    - Deleting and renaming documents
    - Appending content to documents
    - Listing and iterating through documents
    - Document metadata operations

    This service does not handle indexing - that is the responsibility of the IndexService.
    """

    def __init__(self, filesystem_gateway: MarkdownFilesystemGateway) -> None:
        """
        Initialize the DocumentService with a filesystem gateway.

        Parameters
        ----------
        filesystem_gateway : MarkdownFilesystemGateway
            Gateway for file system operations
        """
        self.filesystem_gateway = filesystem_gateway

    def read_document(self, relative_path: str) -> ZkDocument:
        """
        Read a document from the Zettelkasten.

        Parameters
        ----------
        relative_path : str
            The relative path to the document

        Returns
        -------
        ZkDocument
            The document with its metadata and content

        Raises
        ------
        FileNotFoundError
            If the document does not exist
        """
        metadata, content = self.filesystem_gateway.read_markdown(relative_path)
        return ZkDocument(relative_path=relative_path, metadata=metadata, content=content)

    def write_document(self, document: ZkDocument) -> None:
        """
        Write a document to the Zettelkasten, creating or overwriting as needed.

        Parameters
        ----------
        document : ZkDocument
            The document to write

        Raises
        ------
        OSError
            If there are filesystem-related errors (permissions, disk full, etc.)
        yaml.YAMLError
            If there are issues serializing the metadata
        """
        directory = self.filesystem_gateway.get_directory_path(document.relative_path)

        try:
            if not self.filesystem_gateway.path_exists(directory):
                logger.info("Creating directory", directory=directory)
                self.filesystem_gateway.create_directory(directory)

            logger.debug("Writing document", path=document.relative_path)
            try:
                self.filesystem_gateway.write_markdown(document.relative_path, document.metadata, document.content)
                logger.info("Document written successfully", path=document.relative_path)
            except yaml.YAMLError as e:
                logger.error("Failed to serialize document metadata", path=document.relative_path, error=str(e))
                raise

        except OSError as e:
            logger.error("Failed to write document", path=document.relative_path, error=str(e))
            raise

    def delete_document(self, relative_path: str) -> None:
        """
        Delete a document from the Zettelkasten.

        Parameters
        ----------
        relative_path : str
            The relative path to the document to delete

        Raises
        ------
        FileNotFoundError
            If the document does not exist
        OSError
            If there are filesystem-related errors (permissions, etc.)
        """
        logger.info("Deleting document", path=relative_path)

        if not self.document_exists(relative_path):
            logger.error("Document not found", path=relative_path)
            raise FileNotFoundError(f"Document {relative_path} does not exist")

        try:
            self.filesystem_gateway.delete_file(relative_path)
            logger.info("Document deleted successfully", path=relative_path)
        except OSError as e:
            logger.error("Failed to delete document", path=relative_path, error=str(e))
            raise

    def rename_document(self, source_path: str, target_path: str) -> None:
        """
        Rename a document from source path to target path.

        Parameters
        ----------
        source_path : str
            Relative source path of the document to rename
        target_path : str
            Relative target path for the renamed document

        Raises
        ------
        FileNotFoundError
            If the source document doesn't exist
        OSError
            If there are filesystem-related errors (permissions, etc.)
        """
        if not self.document_exists(source_path):
            raise FileNotFoundError(f"Source document {source_path} does not exist")

        self.filesystem_gateway.rename_file(source_path, target_path)

    def list_documents(self) -> list[str]:
        """
        List all document paths in the Zettelkasten.

        Returns
        -------
        list[str]
            List of relative paths to all documents
        """
        return list(self.filesystem_gateway.iterate_markdown_files())

    def iterate_documents(self) -> Iterator[ZkDocument]:
        """
        Iterate through all documents in the Zettelkasten.

        Yields
        ------
        ZkDocument
            Each document in the Zettelkasten
        """
        for relative_path in self.filesystem_gateway.iterate_markdown_files():
            yield self.read_document(relative_path)

    def document_exists(self, relative_path: str) -> bool:
        """
        Check if a document exists at the specified path.

        Parameters
        ----------
        relative_path : str
            The relative path to check

        Returns
        -------
        bool
            True if the document exists, False otherwise
        """
        return self.filesystem_gateway.path_exists(relative_path)

