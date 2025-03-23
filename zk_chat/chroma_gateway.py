import os
from typing import Dict, Optional

import chromadb
from chromadb import Settings
from chromadb.api.configuration import HNSWConfiguration, CollectionConfiguration
from chromadb.api.models.Collection import Collection

from zk_chat.chroma_collections import ZkCollectionName


class ChromaGateway:
    """
    Gateway to Chroma vector database that supports multiple collections.

    This class provides access to different collections in the Chroma database,
    specifically 'excerpts' and 'documents' collections, while maintaining
    backward compatibility with the deprecated 'zettelkasten' collection.
    """

    def __init__(self, db_dir: str = None):
        """
        Initialize the ChromaGateway.

        Args:
            db_dir: The directory where the Chroma database is stored
        """
        # Set default db directory if not provided
        if db_dir is None:
            db_dir = os.path.expanduser("~/.zk_chat_db/")

        # Update Settings with persist_directory
        self.chroma_client = chromadb.PersistentClient(
            path=db_dir,
            settings=Settings(allow_reset=True),
        )

        # Initialize collections dictionary
        self._collections: Dict[ZkCollectionName, Collection] = {}

    def get_collection(self, collection_name: ZkCollectionName) -> Collection:
        """
        Get or create a collection with the specified name.

        Args:
            collection_name: The name of the collection to get or create

        Returns:
            The requested collection
        """
        if collection_name not in self._collections:
            # Create HNSW configuration with cosine distance
            # hnsw_config = HNSWConfiguration(space="cosine")
            # collection_config = CollectionConfiguration(hnsw_configuration=hnsw_config)

            self._collections[collection_name] = self.chroma_client.get_or_create_collection(
                name=collection_name.value,
                metadata={"hsnw:space": "cosine"},
            )
        return self._collections[collection_name]


    def add_items(self, ids, documents, metadatas, embeddings, collection_name: ZkCollectionName = ZkCollectionName.ZETTELKASTEN):
        """
        Add items to a collection.

        Args:
            ids: The IDs of the items to add
            documents: The documents to add
            metadatas: The metadata for each document
            embeddings: The embeddings for each document
            collection_name: The name of the collection to add items to
        """
        collection = self.get_collection(collection_name)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def reset_indexes(self, collection_name: Optional[ZkCollectionName] = None):
        """
        Reset the indexes for a collection or all collections.

        Args:
            collection_name: The name of the collection to reset (resets all if None)
        """
        if collection_name:
            # Reset a specific collection
            try:
                self.chroma_client.delete_collection(collection_name.value)
            except ValueError:
                pass
                # Collection does not exist
            self._collections.pop(collection_name, None)
            self.get_collection(collection_name)
        else:
            # Reset all collections
            self.chroma_client.reset()
            self._collections = {}

    def query(self, query_embeddings, n_results, collection_name: ZkCollectionName = ZkCollectionName.ZETTELKASTEN):
        """
        Query a collection.

        Args:
            query_embeddings: The embeddings to query with
            n_results: The number of results to return
            collection_name: The name of the collection to query

        Returns:
            The query results
        """
        collection = self.get_collection(collection_name)
        return collection.query(query_embeddings=query_embeddings, n_results=n_results)
