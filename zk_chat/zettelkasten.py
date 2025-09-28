import hashlib
from datetime import datetime
from typing import List, Iterator, Any, Optional, Callable

import structlog
import yaml
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument, ZkDocumentExcerpt, ZkQueryExcerptResult, VectorDocumentForStorage, \
    ZkQueryDocumentResult, QueryResult
from zk_chat.rag.splitter import split_tokens
from zk_chat.vector_database import VectorDatabase

logger = structlog.get_logger()

# Type alias for progress callback functions
ProgressCallback = Callable[[str, int, int], None]


class Zettelkasten:
    """
    Manages a Zettelkasten (note-taking system) with vector database integration.

    This class provides functionality for reading, writing, and querying Zettelkasten documents,
    as well as indexing document content for vector search capabilities.
    """
    def __init__(self, tokenizer_gateway: TokenizerGateway, excerpts_db: VectorDatabase,
                 documents_db: VectorDatabase, filesystem_gateway: MarkdownFilesystemGateway):
        self.tokenizer_gateway: TokenizerGateway = tokenizer_gateway
        self.excerpts_db: VectorDatabase = excerpts_db
        self.documents_db: VectorDatabase = documents_db
        self.filesystem_gateway: MarkdownFilesystemGateway = filesystem_gateway

    def _iterate_markdown_files(self) -> Iterator[str]:
        """Yields relative paths for all markdown files in the zk"""
        yield from self.filesystem_gateway.iterate_markdown_files()

    def file_exists(self, relative_path: str) -> bool:
        return self.filesystem_gateway.path_exists(relative_path)

    def document_exists(self, relative_path: str) -> bool:
        return self.file_exists(relative_path)

    def read_document(self, relative_path: str) -> ZkDocument:
        (metadata, content) = self.filesystem_gateway.read_markdown(relative_path)
        document = ZkDocument(
            relative_path=relative_path,
            metadata=metadata,
            content=content
        )
        return document

    def create_or_append_document(self, document: ZkDocument) -> None:
        if self.document_exists(document.relative_path):
            self.append_to_document(document)
        else:
            self.create_or_overwrite_document(document)

    def create_or_overwrite_document(self, document: ZkDocument) -> None:
        """Write a Zettelkasten document to the filesystem.

        Args:
            document: The ZkDocument to write

        Raises:
            OSError: If there are filesystem-related errors (permissions, disk full, etc.)
            yaml.YAMLError: If there are issues dumping the metadata
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
                logger.error("Failed to serialize document metadata",
                             path=document.relative_path,
                             error=str(e))
                raise

        except OSError as e:
            logger.error("Failed to write document",
                         path=document.relative_path,
                         error=str(e))
            raise

    def iterate_documents(self) -> Iterator[ZkDocument]:
        for relative_path in self._iterate_markdown_files():
            yield self.read_document(relative_path)

    def reindex(self, excerpt_size: int = 500, excerpt_overlap: int = 100,
                progress_callback: Optional[ProgressCallback] = None) -> None:
        """Reindex all documents in the Zettelkasten.

        Args:
            excerpt_size: Size of text excerpts for indexing
            excerpt_overlap: Overlap between excerpts
            progress_callback: Optional callback for progress updates (filename, processed_count, total_count)
        """
        self.excerpts_db.reset()
        self.documents_db.reset()

        # Collect all files first to get accurate count for progress
        all_files = list(self._iterate_markdown_files())
        total_files = len(all_files)

        logger.info("Starting reindex", total_files=total_files)

        for i, relative_path in enumerate(all_files):
            if progress_callback:
                progress_callback(relative_path, i + 1, total_files)

            self._index_document(relative_path, excerpt_size, excerpt_overlap)

        logger.info("Reindex completed", processed_files=total_files)

    def update_index(self, since: datetime, excerpt_size: int = 500, excerpt_overlap: int = 100,
                     progress_callback: Optional[ProgressCallback] = None) -> None:
        """Update the index for documents modified since a given date.

        Args:
            since: Only reindex documents modified after this date
            excerpt_size: Size of text excerpts for indexing
            excerpt_overlap: Overlap between excerpts
            progress_callback: Optional callback for progress updates (filename, processed_count, total_count)
        """
        # Pre-scan to find files that need reindexing
        files_to_process = []
        for relative_path in self._iterate_markdown_files():
            if self._needs_reindex(relative_path, since):
                files_to_process.append(relative_path)

        total_files = len(files_to_process)
        logger.info("Starting incremental update", total_files=total_files, since=since)

        for i, relative_path in enumerate(files_to_process):
            if progress_callback:
                progress_callback(relative_path, i + 1, total_files)

            self._index_document(relative_path, excerpt_size, excerpt_overlap)

        logger.info("Incremental update completed", processed_files=total_files)


    def _index_document(self, relative_path: str, excerpt_size: int, excerpt_overlap: int) -> None:
        document = self.read_document(relative_path)
        if document.content:
            self._add_document_to_index(document)
            self._split_document(document, excerpt_size, excerpt_overlap)

    def query_excerpts(self, query: str, n_results: int = 8, max_distance: float = 1.0) -> List[ZkQueryExcerptResult]:
        return [
            self._create_excerpt_query_result(result)
            for result in (self.excerpts_db.query(query, n_results=n_results))
            if result.distance <= max_distance
        ]

    def query_documents(self, query: str, n_results: int = 3, max_distance: float = 0.0) -> List[ZkQueryDocumentResult]:
        """Query the document index for whole documents.

        Args:
            query: The query text
            n_results: The number of results to return
            max_distance: The maximum distance to consider (0.0 means no distance filtering)

        Returns:
            A list of query results
        """
        return [
            self._create_document_query_result(result)
            for result in (self.documents_db.query(query, n_results=n_results))
            if max_distance == 0.0 or result.distance <= max_distance
        ]

    def _create_document_query_result(self, result: QueryResult) -> ZkQueryDocumentResult:
        return ZkQueryDocumentResult(
            document=self.read_document(result.document.id),
            distance=result.distance
        )

    def _create_excerpt_query_result(self, result: QueryResult) -> ZkQueryExcerptResult:
        return ZkQueryExcerptResult(
            excerpt=ZkDocumentExcerpt(
                document_id=result.document.metadata['id'],
                document_title=result.document.metadata['title'],
                text=result.document.content
            ),
            distance=result.distance
        )

    def _split_document(self, document: ZkDocument, excerpt_size: int = 200, excerpt_overlap: int = 100) -> None:
        logger.info("Processing", document_title=document.title)
        tokens = self.tokenizer_gateway.encode(document.content)
        logger.info("Content length", text=len(document.content), tokens=len(tokens))
        token_chunks = split_tokens(tokens, excerpt_size=excerpt_size, excerpt_overlap=excerpt_overlap)
        if len(token_chunks) > 0:
            logger.info("Document split into", n_excerpts=len(token_chunks),
                        excerpt_lengths=[len(chunk) for chunk in token_chunks])
            excerpts = self._decode_tokens_to_text(token_chunks)
            self._add_text_excerpts_to_index(document, excerpts)

    def _add_text_excerpts_to_index(self, document: ZkDocument, text_excerpts: List[str]):
        docs_for_storage = [
            self._create_vector_document_for_storage(excerpt, document)
            for excerpt in text_excerpts
        ]
        self.excerpts_db.add_documents(docs_for_storage)

    def _create_vector_document_for_storage(self, excerpt: str, document: ZkDocument) -> VectorDocumentForStorage:
        return VectorDocumentForStorage(
            id=hashlib.md5(bytes(excerpt, "utf-8")).hexdigest(),
            content=excerpt,
            metadata={
                "id": document.id,
                "title": document.title,
            }
        )

    def _add_document_to_index(self, document: ZkDocument) -> None:
        """Add the whole document to the document index.

        Args:
            document: The ZkDocument to index
        """
        logger.info("Indexing whole document", document_title=document.title)
        doc_for_storage = VectorDocumentForStorage(
            id=document.id,
            content=document.content,
            metadata={
                "id": document.id,
                "title": document.title,
            }
        )
        self.documents_db.add_documents([doc_for_storage])

    def _decode_tokens_to_text(self, token_chunks: List[List[int]]) -> List[str]:
        return [self.tokenizer_gateway.decode(chunk) for chunk in token_chunks]

    def _get_file_mtime(self, relative_path: str) -> datetime:
        return self.filesystem_gateway.get_modified_time(relative_path)

    def _needs_reindex(self, relative_path: str, since: datetime) -> bool:
        return self._get_file_mtime(relative_path) > since

    def _merge_metadata(self, original_metadata: dict[str, Any], new_metadata: dict[str, Any]) -> dict[str, Any]:
        """Merge two metadata dictionaries with special handling for nested structures and arrays.

        Args:
            original_metadata: The original metadata dictionary
            new_metadata: The new metadata to merge

        Returns:
            dict: The merged metadata
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

    def append_to_document(self, document: ZkDocument) -> None:
        """Append content to an existing document and merge metadata.

        Args:
            document: The document containing content to append and metadata to merge
        """
        original = self.read_document(document.relative_path)
        merged_content = original.content + f"\n\n---\n\n{document.content}"
        merged_metadata = self._merge_metadata(original.metadata, document.metadata)
        merged_document = ZkDocument(
            relative_path=original.relative_path,
            metadata=merged_metadata,
            content=merged_content
        )
        self.create_or_overwrite_document(merged_document)

    def rename_document(self, source_path: str, target_path: str) -> None:
        """Rename a document from source path to target path.

        Args:
            source_path: Relative source path of the document to rename
            target_path: Relative target path for the renamed document

        Raises:
            FileNotFoundError: If the source document doesn't exist
            OSError: If there are filesystem-related errors (permissions, etc.)
        """
        if not self.document_exists(source_path):
            raise FileNotFoundError(f"Source document {source_path} does not exist")

        self.filesystem_gateway.rename_file(source_path, target_path)

    def delete_document(self, relative_path: str) -> None:
        """Delete a document at the specified path.

        Args:
            relative_path: Relative path of the document to delete

        Raises:
            FileNotFoundError: If the document doesn't exist
            OSError: If there are filesystem-related errors (permissions, etc.)
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
