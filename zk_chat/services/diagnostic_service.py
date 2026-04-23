"""Service for gathering diagnostic data about the index."""

from typing import Any

from pydantic import BaseModel

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway


class CollectionStatus(BaseModel):
    name: str
    count: int | None = None
    status: str
    error: str | None = None


class SampleEntry(BaseModel):
    id: str
    title: str
    content_preview: str


class CollectionSamples(BaseModel):
    collection_name: str
    total_count: int
    entries: list[SampleEntry]


class EmbeddingTestResult(BaseModel):
    success: bool
    dimensions: int | None = None
    sample_values: list[float] | None = None
    error: str | None = None


class DiagnosticService:
    """Gathers diagnostic data from ChromaDB collections without performing any I/O output."""

    def __init__(self, chroma: ChromaGateway) -> None:
        self._chroma = chroma

    def get_collection_statuses(self) -> list[CollectionStatus]:
        """Return status information for each known collection."""
        statuses = []
        for collection_name in [ZkCollectionName.DOCUMENTS, ZkCollectionName.EXCERPTS]:
            try:
                collection = self._chroma.get_collection(collection_name)
                count = collection.count()
                status = "✓ OK" if count > 0 else "⚠ Empty"
                statuses.append(CollectionStatus(name=collection_name.value, count=count, status=status))
            except (ValueError, OSError) as e:
                statuses.append(
                    CollectionStatus(name=collection_name.value, status=f"✗ Error: {e}", error=str(e))
                )
        return statuses

    def get_sample_documents(self, limit: int = 3) -> list[CollectionSamples]:
        """Return sample documents from each collection."""
        samples = []
        for collection_name in [ZkCollectionName.DOCUMENTS, ZkCollectionName.EXCERPTS]:
            try:
                collection = self._chroma.get_collection(collection_name)
                count = collection.count()
                if count > 0:
                    results = collection.get(limit=limit, include=["metadatas", "documents"])
                    entries = [
                        SampleEntry(
                            id=doc_id,
                            title=metadata.get("title", "N/A"),
                            content_preview=document[:100],
                        )
                        for doc_id, metadata, document in zip(
                            results["ids"], results["metadatas"], results["documents"], strict=False
                        )
                    ]
                    samples.append(
                        CollectionSamples(
                            collection_name=collection_name.value,
                            total_count=count,
                            entries=entries,
                        )
                    )
                else:
                    samples.append(
                        CollectionSamples(collection_name=collection_name.value, total_count=0, entries=[])
                    )
            except (ValueError, OSError):
                samples.append(
                    CollectionSamples(collection_name=collection_name.value, total_count=0, entries=[])
                )
        return samples

    def test_embedding(self, gateway: Any, test_text: str = "This is a test document") -> EmbeddingTestResult:
        """Test embedding generation via the given model gateway."""
        try:
            embedding = gateway.calculate_embeddings(test_text)
            return EmbeddingTestResult(
                success=True,
                dimensions=len(embedding),
                sample_values=list(embedding[:3]),
            )
        except (ConnectionError, OSError, ValueError) as e:
            return EmbeddingTestResult(success=False, error=str(e))
