from typing import List

import structlog
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from zk_chat.models import VectorDocumentForStorage, VectorDocumentWithEmbeddings, QueryResult
from zk_chat.chroma_gateway import ChromaGateway

logger = structlog.get_logger()

class VectorDatabase:
    def __init__(self, chroma_gateway: ChromaGateway, embeddings_gateway: EmbeddingsGateway):
        self.chroma_gateway = chroma_gateway
        self.embeddings_gateway = embeddings_gateway

    def add_documents(self, documents: List[VectorDocumentForStorage]):
        vector_docs = [
            VectorDocumentWithEmbeddings.from_document(doc, self.embeddings_gateway.calculate(doc.content))
            for doc in documents
        ]
        
        self.chroma_gateway.add_items(
            ids=[doc.id for doc in vector_docs],
            documents=[doc.content for doc in vector_docs],
            metadatas=[doc.metadata for doc in vector_docs],
            embeddings=[doc.embedding for doc in vector_docs]
        )

    def reset(self):
        self.chroma_gateway.reset_indexes()

    def query(self, query_text: str, n_results: int) -> List[QueryResult]:
        query_embedding = self.embeddings_gateway.calculate(query_text)
        results = self.chroma_gateway.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        
        query_results = []
        for i in range(len(results['ids'][0])):
            doc = VectorDocumentForStorage(
                id=results['ids'][0][i],
                content=results['documents'][0][i],
                metadata=results['metadatas'][0][i]
            )
            distance = results['distances'][0][i]
            query_results.append(QueryResult(document=doc, distance=distance))

        logger.info(
            "Vector query results",
            extra = {
                "query_text": query_text,
                "num_results": len(query_results),
                "min_distance": min(r.distance for r in query_results) if query_results else None,
                "max_distance": max(r.distance for r in query_results) if query_results else None
            }
        )

        return query_results
