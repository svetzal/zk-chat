import os
import re
from typing import Any

from pydantic import BaseModel, Field


class ZkDocument(BaseModel):
    """A markdown document loaded from the Zettelkasten vault."""

    relative_path: str
    metadata: dict[str, Any]
    content: str

    @property
    def title(self) -> str:
        """Human-readable title derived from the filename with leading ``@``/``!`` identifier prefixes stripped."""
        return self._strip_identifier_prefix(self._base_filename_without_extension())

    @property
    def id(self) -> str:
        return self.relative_path

    def _strip_identifier_prefix(self, string: str) -> str:
        return re.sub(r"^[@!]\s*", "", string)

    def _base_filename_without_extension(self) -> str:
        return os.path.splitext(os.path.basename(self.relative_path))[0]


class ZkDocumentExcerpt(BaseModel):
    """A text excerpt taken from a vault document, used as the unit of vector search."""

    document_id: str
    document_title: str
    text: str


class ZkQueryExcerptResult(BaseModel):
    """An excerpt returned by a semantic search, paired with its similarity distance."""

    excerpt: ZkDocumentExcerpt
    distance: float


class ZkQueryDocumentResult(BaseModel):
    """A full document returned by a semantic search, paired with its similarity distance."""

    document: ZkDocument
    distance: float


class VectorDocument(BaseModel):
    """A document with the fields required for storage in and retrieval from a vector database."""

    id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="The text content")
    metadata: dict[str, Any] = Field(..., description="Additional metadata about the document")


class VectorDocumentForStorage(VectorDocument):
    """Document ready for storage, before embedding calculation"""

    pass


class QueryResult(BaseModel):
    """Document with its distance from the query vector"""

    document: VectorDocumentForStorage
    distance: float


class VectorDocumentWithEmbeddings(VectorDocument):
    """Document with calculated embeddings, ready for vector database storage"""

    embedding: list[float] = Field(..., description="The vector embedding of the content")

    @classmethod
    def from_document(
        cls, document: VectorDocumentForStorage, embedding: list[float]
    ) -> "VectorDocumentWithEmbeddings":
        """Create an instance by attaching a pre-computed embedding to an existing document.

        Parameters
        ----------
        document : VectorDocumentForStorage
            The source document whose id, content, and metadata are copied.
        embedding : list[float]
            The vector embedding calculated for the document's content.

        Returns
        -------
        VectorDocumentWithEmbeddings
            A new instance combining the document fields with the provided embedding.
        """
        return cls(id=document.id, content=document.content, metadata=document.metadata, embedding=embedding)
