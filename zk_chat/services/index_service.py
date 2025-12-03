"""
Index Service for Zettelkasten

This service provides functionality for vector indexing and semantic search in a Zettelkasten.
It handles document indexing, excerpt creation, and query operations using vector databases.
"""
import hashlib
from collections.abc import Callable
from datetime import datetime

import structlog
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
from pydantic import BaseModel

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import (
    QueryResult,
    VectorDocumentForStorage,
    ZkDocument,
    ZkDocumentExcerpt,
    ZkQueryDocumentResult,
    ZkQueryExcerptResult,
)
from zk_chat.rag.splitter import split_tokens
from zk_chat.vector_database import VectorDatabase

logger = structlog.get_logger()

# Type alias for progress callback functions
ProgressCallback = Callable[[str, int, int], None]


class IndexStats(BaseModel):
    """Statistics about the index state."""
    total_documents: int
    total_excerpts: int
    last_indexed: datetime | None


class IndexService:
    """
    Service for managing vector indexing and semantic search in a Zettelkasten.

    Handles operations including:
    - Full and incremental reindexing
    - Document and excerpt indexing
    - Semantic search queries
    - Index statistics

    This service does not handle document CRUD - that is the responsibility of DocumentService.
    """

    def __init__(self,
                 tokenizer_gateway: TokenizerGateway,
                 excerpts_db: VectorDatabase,
                 documents_db: VectorDatabase,
                 filesystem_gateway: MarkdownFilesystemGateway):
        """
        Initialize the IndexService with required dependencies.

        Parameters
        ----------
        tokenizer_gateway : TokenizerGateway
            Gateway for tokenization operations
        excerpts_db : VectorDatabase
            Vector database for document excerpts
        documents_db : VectorDatabase
            Vector database for whole documents
        filesystem_gateway : MarkdownFilesystemGateway
            Gateway for filesystem operations
        """
        self.tokenizer_gateway = tokenizer_gateway
        self.excerpts_db = excerpts_db
        self.documents_db = documents_db
        self.filesystem_gateway = filesystem_gateway
        self._last_indexed: datetime | None = None

    def reindex_all(self, excerpt_size: int = 500, excerpt_overlap: int = 100,
                    progress_callback: ProgressCallback | None = None) -> None:
        """
        Reindex all documents in the Zettelkasten.

        Parameters
        ----------
        excerpt_size : int, optional
            Size of text excerpts for indexing, by default 500
        excerpt_overlap : int, optional
            Overlap between excerpts, by default 100
        progress_callback : ProgressCallback, optional
            Optional callback for progress updates (filename, processed_count, total_count)
        """
        self.excerpts_db.reset()
        self.documents_db.reset()

        all_files = list(self.filesystem_gateway.iterate_markdown_files())
        total_files = len(all_files)

        logger.info("Starting reindex", total_files=total_files)

        for i, relative_path in enumerate(all_files):
            if progress_callback:
                progress_callback(relative_path, i + 1, total_files)

            self._index_document(relative_path, excerpt_size, excerpt_overlap)

        self._last_indexed = datetime.now()
        logger.info("Reindex completed", processed_files=total_files)

    def update_index(self, since: datetime, excerpt_size: int = 500, excerpt_overlap: int = 100,
                     progress_callback: ProgressCallback | None = None) -> None:
        """
        Update the index for documents modified since a given date.

        Parameters
        ----------
        since : datetime
            Only reindex documents modified after this date
        excerpt_size : int, optional
            Size of text excerpts for indexing, by default 500
        excerpt_overlap : int, optional
            Overlap between excerpts, by default 100
        progress_callback : ProgressCallback, optional
            Optional callback for progress updates (filename, processed_count, total_count)
        """
        files_to_process = []
        for relative_path in self.filesystem_gateway.iterate_markdown_files():
            if self._needs_reindex(relative_path, since):
                files_to_process.append(relative_path)

        total_files = len(files_to_process)
        logger.info("Starting incremental update", total_files=total_files, since=since)

        for i, relative_path in enumerate(files_to_process):
            if progress_callback:
                progress_callback(relative_path, i + 1, total_files)

            self._index_document(relative_path, excerpt_size, excerpt_overlap)

        self._last_indexed = datetime.now()
        logger.info("Incremental update completed", processed_files=total_files)

    def index_document(self, relative_path: str, excerpt_size: int = 500,
                       excerpt_overlap: int = 100) -> None:
        """
        Index a single document.

        Parameters
        ----------
        relative_path : str
            Path to the document to index
        excerpt_size : int, optional
            Size of text excerpts for indexing, by default 500
        excerpt_overlap : int, optional
            Overlap between excerpts, by default 100
        """
        self._index_document(relative_path, excerpt_size, excerpt_overlap)

    def remove_document_from_index(self, relative_path: str) -> None:
        """
        Remove a document from the index.

        Note: This is a placeholder for future implementation. Currently,
        ChromaDB doesn't support efficient single document removal without
        knowing all the excerpt IDs.

        Parameters
        ----------
        relative_path : str
            Path to the document to remove from index
        """
        logger.warning("Document removal from index not yet implemented",
                       path=relative_path)

    def query_excerpts(self, query: str, n_results: int = 8,
                       max_distance: float = 1.0) -> list[ZkQueryExcerptResult]:
        """
        Query the excerpt index for relevant text excerpts.

        Parameters
        ----------
        query : str
            The query text
        n_results : int, optional
            The number of results to return, by default 8
        max_distance : float, optional
            The maximum distance to consider, by default 1.0

        Returns
        -------
        list[ZkQueryExcerptResult]
            A list of query results with excerpts
        """
        return [
            self._create_excerpt_query_result(result)
            for result in self.excerpts_db.query(query, n_results=n_results)
            if result.distance <= max_distance
        ]

    def query_documents(self, query: str, n_results: int = 3,
                        max_distance: float = 0.0) -> list[ZkQueryDocumentResult]:
        """
        Query the document index for whole documents.

        Parameters
        ----------
        query : str
            The query text
        n_results : int, optional
            The number of results to return, by default 3
        max_distance : float, optional
            The maximum distance to consider (0.0 means no distance filtering), by default 0.0

        Returns
        -------
        list[ZkQueryDocumentResult]
            A list of query results with documents
        """
        results = []
        for result in self.documents_db.query(query, n_results=n_results):
            if max_distance != 0.0 and result.distance > max_distance:
                continue
            query_result = self._create_document_query_result(result)
            if query_result is not None:
                results.append(query_result)
        return results

    def get_index_stats(self) -> IndexStats:
        """
        Get statistics about the current index state.

        Returns
        -------
        IndexStats
            Statistics about the index
        """
        total_documents = sum(1 for _ in self.filesystem_gateway.iterate_markdown_files())
        return IndexStats(
            total_documents=total_documents,
            total_excerpts=0,  # Would need Chroma API to get actual count
            last_indexed=self._last_indexed
        )

    def _index_document(self, relative_path: str, excerpt_size: int,
                        excerpt_overlap: int) -> None:
        """Index a single document by reading and processing it."""
        document = self._read_document(relative_path)
        if document.content:
            self._add_document_to_index(document)
            self._split_document(document, excerpt_size, excerpt_overlap)

    def _read_document(self, relative_path: str) -> ZkDocument:
        """Read a document from the filesystem."""
        metadata, content = self.filesystem_gateway.read_markdown(relative_path)
        return ZkDocument(
            relative_path=relative_path,
            metadata=metadata,
            content=content
        )

    def _split_document(self, document: ZkDocument, excerpt_size: int = 200,
                        excerpt_overlap: int = 100) -> None:
        """Split a document into excerpts and index them."""
        logger.info("Processing", document_title=document.title)
        tokens = self.tokenizer_gateway.encode(document.content)
        logger.info("Content length", text=len(document.content), tokens=len(tokens))
        token_chunks = split_tokens(tokens, excerpt_size=excerpt_size,
                                    excerpt_overlap=excerpt_overlap)
        if len(token_chunks) > 0:
            logger.info("Document split into", n_excerpts=len(token_chunks),
                        excerpt_lengths=[len(chunk) for chunk in token_chunks])
            excerpts = self._decode_tokens_to_text(token_chunks)
            self._add_text_excerpts_to_index(document, excerpts)

    def _add_text_excerpts_to_index(self, document: ZkDocument,
                                    text_excerpts: list[str]) -> None:
        """Add text excerpts to the excerpts index."""
        docs_for_storage = [
            self._create_vector_document_for_storage(excerpt, document)
            for excerpt in text_excerpts
        ]
        self.excerpts_db.add_documents(docs_for_storage)

    def _create_vector_document_for_storage(self, excerpt: str,
                                            document: ZkDocument) -> VectorDocumentForStorage:
        """Create a vector document for storage from an excerpt."""
        return VectorDocumentForStorage(
            id=hashlib.md5(bytes(excerpt, "utf-8")).hexdigest(),
            content=excerpt,
            metadata={
                "id": document.id,
                "title": document.title,
            }
        )

    def _add_document_to_index(self, document: ZkDocument) -> None:
        """Add the whole document to the document index."""
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

    def _decode_tokens_to_text(self, token_chunks: list[list[int]]) -> list[str]:
        """Decode token chunks back to text."""
        return [self.tokenizer_gateway.decode(chunk) for chunk in token_chunks]

    def _get_file_mtime(self, relative_path: str) -> datetime:
        """Get the modification time of a file."""
        return self.filesystem_gateway.get_modified_time(relative_path)

    def _needs_reindex(self, relative_path: str, since: datetime) -> bool:
        """Check if a file needs reindexing based on modification time."""
        return self._get_file_mtime(relative_path) > since

    def _create_excerpt_query_result(self, result: QueryResult) -> ZkQueryExcerptResult:
        """Create an excerpt query result from a query result."""
        return ZkQueryExcerptResult(
            excerpt=ZkDocumentExcerpt(
                document_id=result.document.metadata['id'],
                document_title=result.document.metadata['title'],
                text=result.document.content
            ),
            distance=result.distance
        )

    def _create_document_query_result(self, result: QueryResult) -> ZkQueryDocumentResult | None:
        """Create a document query result, returning None if the document no longer exists."""
        try:
            document = self._read_document(result.document.id)
            return ZkQueryDocumentResult(
                document=document,
                distance=result.distance
            )
        except FileNotFoundError:
            logger.warning("Document in index not found on filesystem",
                           document_id=result.document.id)
            return None
