import hashlib
from datetime import datetime
from typing import List, Iterator

import structlog
import yaml
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.filesystem_gateway import FilesystemGateway
from zk_chat.markdown.loader import load_markdown
from zk_chat.models import ZkDocument, ZkDocumentExcerpt, ZkQueryResult, VectorDocumentForStorage
from zk_chat.rag.splitter import split_tokens
from zk_chat.vector_database import VectorDatabase

logger = structlog.get_logger()


class Zettelkasten:
    def __init__(self,
                 tokenizer_gateway: TokenizerGateway,
                 vector_db: VectorDatabase,
                 filesystem_gateway: FilesystemGateway):
        self.tokenizer_gateway: TokenizerGateway = tokenizer_gateway
        self.vector_db: VectorDatabase = vector_db
        self.filesystem_gateway: FilesystemGateway = filesystem_gateway

    def _iterate_markdown_files(self) -> Iterator[str]:
        """Yields relative paths for all markdown files in the zk"""
        yield from self.filesystem_gateway.iterate_markdown_files()

    def document_exists(self, relative_path: str) -> bool:
        return self.filesystem_gateway.path_exists(relative_path)

    def read_document(self, relative_path: str) -> ZkDocument:
        (metadata, content) = load_markdown(self.filesystem_gateway.get_full_path(relative_path))
        document = ZkDocument(
            relative_path=relative_path,
            metadata=metadata,
            content=content
        )
        return document

    def create_or_append_document(self, document: ZkDocument):
        if self.document_exists(document.relative_path):
            self.append_to_document(document)
        else:
            self.create_or_overwrite_document(document)

    def create_or_overwrite_document(self, document: ZkDocument):
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

            # Try to serialize metadata before writing the file
            try:
                metadata_yaml = yaml.dump(document.metadata, Dumper=yaml.SafeDumper)
            except yaml.YAMLError as e:
                logger.error("Failed to serialize document metadata",
                             path=document.relative_path,
                             error=str(e))
                raise

            content = f"---\n{metadata_yaml}---\n{document.content}"
            logger.debug("Writing document", path=document.relative_path)
            self.filesystem_gateway.write_file(document.relative_path, content)
            logger.info("Document written successfully", path=document.relative_path)

        except OSError as e:
            logger.error("Failed to write document",
                         path=document.relative_path,
                         error=str(e))
            raise
        except yaml.YAMLError as e:
            logger.error("Failed to serialize document metadata",
                         path=document.relative_path,
                         error=str(e))
            raise

    def iterate_documents(self) -> Iterator[ZkDocument]:
        for relative_path in self._iterate_markdown_files():
            yield self.read_document(relative_path)

    def split_and_index(self, excerpt_size=500, excerpt_overlap=100):
        self.vector_db.reset()
        for relative_path in self._iterate_markdown_files():
            document = self.read_document(relative_path)
            self._split_document(document, excerpt_size, excerpt_overlap)

    def incremental_split_and_index(self, since: datetime, excerpt_size=500, excerpt_overlap=100):
        for relative_path in self._iterate_markdown_files():
            if self._needs_reindex(relative_path, since):
                document = self.read_document(relative_path)
                self._split_document(document, excerpt_size, excerpt_overlap)

    def query_excerpts(self, query: str, n_results: int = 5, max_distance: float = 1.0) -> List[ZkQueryResult]:
        return [
            self._create_query_result(result)
            for result in (self.vector_db.query(query, n_results=n_results))
            if result.distance <= max_distance
        ]

    def _create_query_result(self, result):
        return ZkQueryResult(
            excerpt=ZkDocumentExcerpt(
                document_id=result.document.metadata['id'],
                document_title=result.document.metadata['title'],
                text=result.document.content
            ),
            distance=result.distance
        )

    def _split_document(self, document, excerpt_size=200, excerpt_overlap=100):
        logger.info(f"Processing", document_title=document.title)
        tokens = self.tokenizer_gateway.encode(document.content)
        logger.info("Content length", text=len(document.content), tokens=len(tokens))
        token_chunks = split_tokens(tokens, excerpt_size=excerpt_size, excerpt_overlap=excerpt_overlap)
        if len(token_chunks) > 0:
            logger.info("Document split into", n_excerpts=len(token_chunks),
                        excerpt_lengths=[len(chunk) for chunk in token_chunks])
            excerpts = self._decode_tokens_to_text(token_chunks)
            self._add_text_excerpts_to_index(document, excerpts)

    def _add_text_excerpts_to_index(self, document, text_excerpts):
        docs_for_storage = [
            self._create_vector_document_for_storage(excerpt, document)
            for excerpt in text_excerpts
        ]
        self.vector_db.add_documents(docs_for_storage)

    def _create_vector_document_for_storage(self, excerpt, document):
        return VectorDocumentForStorage(
            id=hashlib.md5(bytes(excerpt, "utf-8")).hexdigest(),
            content=excerpt,
            metadata={
                "id": document.id,
                "title": document.title,
            }
        )

    def _decode_tokens_to_text(self, token_chunks):
        return [self.tokenizer_gateway.decode(chunk) for chunk in token_chunks]

    def _get_file_mtime(self, relative_path: str) -> datetime:
        return self.filesystem_gateway.get_modified_time(relative_path)

    def _needs_reindex(self, relative_path: str, since: datetime) -> bool:
        return self._get_file_mtime(relative_path) > since

    def _merge_metadata(self, original_metadata: dict, new_metadata: dict) -> dict:
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

    def append_to_document(self, document: ZkDocument):
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
