import os
import re
from typing import List, Any

from pydantic import BaseModel, Field


class ZkDocument(BaseModel):
    relative_path: str
    metadata: dict[str,Any]
    content: str

    @property
    def title(self) -> str:
        return self._strip_identifier_prefix(self._base_filename_without_extension())

    @property
    def id(self) -> str:
        return self.relative_path

    def _strip_identifier_prefix(self, string):
        return re.sub(r'^[@!]\s*', '', string)

    def _base_filename_without_extension(self):
        return os.path.splitext(os.path.basename(self.relative_path))[0]


class ZkDocumentExcerpt(BaseModel):
    document_id: str
    document_title: str
    text: str


class ZkQueryResult(BaseModel):
    excerpt: ZkDocumentExcerpt
    distance: float


class VectorDocument(BaseModel):
    id: str = Field(..., description="Unique identifier for the document")
    content: str = Field(..., description="The text content")
    metadata: dict = Field(..., description="Additional metadata about the document")


class VectorDocumentForStorage(VectorDocument):
    """Document ready for storage, before embedding calculation"""
    pass


class QueryResult(BaseModel):
    """Document with its distance from the query vector"""
    document: VectorDocumentForStorage
    distance: float


class VectorDocumentWithEmbeddings(VectorDocument):
    """Document with calculated embeddings, ready for vector database storage"""
    embedding: List[float] = Field(..., description="The vector embedding of the content")

    @classmethod
    def from_document(cls, document: VectorDocumentForStorage,
                      embedding: List[float]) -> 'VectorDocumentWithEmbeddings':
        return cls(
            id=document.id,
            content=document.content,
            metadata=document.metadata,
            embedding=embedding
        )
