import uuid
from typing import Union

import structlog
from mojentic.llm.gateways import OllamaGateway, OpenAIGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.chroma_collections import ZkCollectionName

logger = structlog.get_logger()


class SmartMemory:
    """
    A memory system that stores and retrieves information using vector embeddings.
    """

    def __init__(self, chroma_gateway: ChromaGateway, gateway: Union[OllamaGateway, OpenAIGateway]):
        """
        Initialize SmartMemory with a ChromaGateway and a gateway for embeddings.

        Args:
            chroma_gateway: The gateway to the Chroma vector database
            gateway: The gateway for calculating embeddings (OllamaGateway or OpenAIGateway)
        """
        self.chroma = chroma_gateway
        self.gateway = gateway
        self.collection_name = ZkCollectionName.SMART_MEMORY

    def store(self, information: str):
        """
        Store information in smart memory.

        Args:
            information: The information to store
        """
        embeddings = self.gateway.calculate_embeddings(information)

        id = str(uuid.uuid4())
        logger.info("Storing information in smart memory", id=id, information=information, embeddings=embeddings)
        self.chroma.add_items(
            ids=[id],
            documents=[information],
            metadatas=None,
            embeddings=[embeddings],
            collection_name=self.collection_name
        )

    def retrieve(self, query: str, n_results: int = 5):
        """
        Retrieve information from smart memory based on a query.

        Args:
            query: The query to search for
            n_results: The number of results to return

        Returns:
            The query results
        """
        query_embeddings = self.gateway.calculate_embeddings(query)
        results = self.chroma.query(
            query_embeddings=query_embeddings, 
            n_results=n_results,
            collection_name=self.collection_name
        )
        logger.info("Retrieved information from smart memory", query=query, n_results=n_results, results=results)
        return results

    def reset(self):
        """
        Reset the smart memory by clearing all stored information.
        """
        logger.info("Resetting smart memory")
        self.chroma.reset_indexes(collection_name=self.collection_name)
