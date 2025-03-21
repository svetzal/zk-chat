from typing import List

import structlog
from chromadb.api.models.Collection import CollectionName
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.models import VectorDocumentForStorage, VectorDocumentWithEmbeddings, QueryResult
from zk_chat.chroma_gateway import ChromaGateway

logger = structlog.get_logger()

class VectorDatabase:

    chroma_gateway: ChromaGateway
    embeddings_gateway: EmbeddingsGateway
    collection_name: ZkCollectionName

    def __init__(self, chroma_gateway: ChromaGateway, embeddings_gateway: EmbeddingsGateway, collection_name: ZkCollectionName):
        """
        Initialize the VectorDatabase with a ChromaGateway and EmbeddingsGateway.

        Args:
            chroma_gateway: The gateway to the Chroma vector database
            embeddings_gateway: The gateway for calculating embeddings
            collection_name: The name of the collection to use
        """
        self.chroma_gateway = chroma_gateway
        self.embeddings_gateway = embeddings_gateway
        self.collection_name = collection_name

    def add_documents(self, documents: List[VectorDocumentForStorage]):
        """
        Add documents to the vector database.

        Args:
            documents: The documents to add
        """
        vector_docs = [
            VectorDocumentWithEmbeddings.from_document(doc, self.embeddings_gateway.calculate(doc.content))
            for doc in documents
        ]

        self.chroma_gateway.add_items(
            ids=[doc.id for doc in vector_docs],
            documents=[doc.content for doc in vector_docs],
            metadatas=[doc.metadata for doc in vector_docs],
            embeddings=[doc.embedding for doc in vector_docs],
            collection_name=self.collection_name
        )

    def reset(self):
        """
        Reset the vector database.
        """
        self.chroma_gateway.reset_indexes(collection_name=self.collection_name)

    def query(self, query_text: str, n_results: int) -> List[QueryResult]:
        """
        Query the vector database.

        Args:
            query_text: The text to query with
            n_results: The number of results to return

        Returns:
            A list of query results
        """
        query_embedding = self.embeddings_gateway.calculate(query_text)
        results = self.chroma_gateway.query(
            query_embeddings=query_embedding,
            n_results=n_results,
            collection_name=self.collection_name
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
