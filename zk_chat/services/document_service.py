"""
Document Service for Zettelkasten

This service provides functionality for document lifecycle operations in a Zettelkasten.
It handles document CRUD operations without indexing concerns, delegating file system
operations to the MarkdownFilesystemGateway.
"""

from collections.abc import Iterator
from typing import Any

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

    def __init__(self, filesystem_gateway: MarkdownFilesystemGateway):
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

    def append_to_document(self, document: ZkDocument) -> None:
        """
        Append content to an existing document and merge metadata.

        Parameters
        ----------
        document : ZkDocument
            The document containing content to append and metadata to merge

        Raises
        ------
        FileNotFoundError
            If the document does not exist
        """
        original = self.read_document(document.relative_path)
        merged_content = original.content + f"\n\n---\n\n{document.content}"
        merged_metadata = self._merge_metadata(original.metadata, document.metadata)
        merged_document = ZkDocument(
            relative_path=original.relative_path, metadata=merged_metadata, content=merged_content
        )
        self.write_document(merged_document)

    def create_or_append_document(self, document: ZkDocument) -> None:
        """
        Create a new document or append to an existing one.

        Parameters
        ----------
        document : ZkDocument
            The document to create or append to
        """
        if self.document_exists(document.relative_path):
            self.append_to_document(document)
        else:
            self.write_document(document)

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

    def get_document_metadata(self, relative_path: str) -> dict[str, Any]:
        """
        Get the metadata for a document without reading the full content.

        Parameters
        ----------
        relative_path : str
            The relative path to the document

        Returns
        -------
        dict[str, Any]
            The document's metadata

        Raises
        ------
        FileNotFoundError
            If the document does not exist
        """
        metadata, _ = self.filesystem_gateway.read_markdown(relative_path)
        return metadata

    def update_document_metadata(self, relative_path: str, metadata: dict[str, Any]) -> None:
        """
        Update the metadata for a document, merging with existing metadata.

        Parameters
        ----------
        relative_path : str
            The relative path to the document
        metadata : dict[str, Any]
            The metadata to merge with existing metadata

        Raises
        ------
        FileNotFoundError
            If the document does not exist
        """
        document = self.read_document(relative_path)
        merged_metadata = self._merge_metadata(document.metadata, metadata)
        updated_document = ZkDocument(relative_path=relative_path, metadata=merged_metadata, content=document.content)
        self.write_document(updated_document)

    def _merge_metadata(self, original_metadata: dict[str, Any], new_metadata: dict[str, Any]) -> dict[str, Any]:
        """
        Merge two metadata dictionaries with special handling for nested structures and arrays.

        Parameters
        ----------
        original_metadata : dict[str, Any]
            The original metadata dictionary
        new_metadata : dict[str, Any]
            The new metadata to merge

        Returns
        -------
        dict[str, Any]
            The merged metadata
        """
        result = original_metadata.copy()

        for key, new_value in new_metadata.items():
            if key not in result:
                result[key] = new_value
                continue

            original_value = result[key]

            # Handle None values
            if original_value is None:
                result[key] = new_value
                continue

            if new_value is None:
                continue

            # Handle lists (arrays)
            if isinstance(original_value, list) and isinstance(new_value, list):
                result[key] = list(set(original_value + new_value))
                continue

            # Handle nested dictionaries
            if isinstance(original_value, dict) and isinstance(new_value, dict):
                result[key] = self._merge_metadata(original_value, new_value)
                continue

            # For different types or simple values, new value takes precedence
            result[key] = new_value

        return result
