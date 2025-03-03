import uuid

import structlog
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway

from zk_chat.chroma_gateway import ChromaGateway

logger = structlog.get_logger()


class SmartMemory:
    def __init__(self, chroma_gateway: ChromaGateway, embeddings_gateway: EmbeddingsGateway):
        self.chroma = chroma_gateway
        self.embeddings = embeddings_gateway

    def store(self, information: str):
        embeddings = self.embeddings.calculate(information)
        id = str(uuid.uuid4())
        logger.info("Storing information in smart memory", id=id, information=information, embeddings=embeddings)
        self.chroma.add_items(
            ids=[id],
            documents=[information],
            metadatas=None,
            embeddings=[embeddings]
        )

    def retrieve(self, query: str, n_results: int = 5):
        query_embeddings = self.embeddings.calculate(query)
        results = self.chroma.query(query_embeddings=query_embeddings, n_results=n_results)
        logger.info("Retrieved information from smart memory", query=query, n_results=n_results, results=results)
        return results

    def reset(self):
        """Reset the smart memory by clearing all stored information."""
        logger.info("Resetting smart memory")
        self.chroma.reset_indexes()
