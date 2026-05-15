from collections.abc import Iterator

import structlog
import yaml

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument

logger = structlog.get_logger()


class DocumentService:
    """Handles document CRUD operations; does not handle indexing."""

    def __init__(self, filesystem_gateway: MarkdownFilesystemGateway) -> None:
        self.filesystem_gateway = filesystem_gateway

    def read_document(self, relative_path: str) -> ZkDocument:
        metadata, content = self.filesystem_gateway.read_markdown(relative_path)
        return ZkDocument(relative_path=relative_path, metadata=metadata, content=content)

    def write_document(self, document: ZkDocument) -> None:
        """Creates or overwrites the document, creating parent directories as needed."""
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
        """Raises FileNotFoundError if the source document does not exist."""
        if not self.document_exists(source_path):
            raise FileNotFoundError(f"Source document {source_path} does not exist")

        self.filesystem_gateway.rename_file(source_path, target_path)

    def list_documents(self) -> list[str]:
        return list(self.filesystem_gateway.iterate_markdown_files())

    def iterate_documents(self) -> Iterator[ZkDocument]:
        for relative_path in self.filesystem_gateway.iterate_markdown_files():
            yield self.read_document(relative_path)

    def document_exists(self, relative_path: str) -> bool:
        return self.filesystem_gateway.path_exists(relative_path)

