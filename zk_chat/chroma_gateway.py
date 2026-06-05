import os

import chromadb
from chromadb import Settings
from chromadb.api.models.Collection import Collection

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.config import ModelGateway


class ChromaGateway:
    """
    Gateway to Chroma vector database that supports multiple collections.

    This class provides access to different collections in the Chroma database,
    specifically 'excerpts' and 'documents' collections, while maintaining
    backward compatibility with the deprecated 'zettelkasten' collection.
    """

    def __init__(self, gateway: ModelGateway, db_dir: str) -> None:
        self.chroma_client = chromadb.PersistentClient(
            path=os.path.join(db_dir, gateway.value),
            settings=Settings(allow_reset=True),
        )

        self._collections: dict[ZkCollectionName, Collection] = {}

    def get_collection(self, collection_name: ZkCollectionName) -> Collection:
        """Return the named ChromaDB collection, creating it if it does not yet exist."""
        if collection_name not in self._collections:
            self._collections[collection_name] = self.chroma_client.get_or_create_collection(
                name=collection_name.value,
                metadata={"hsnw:space": "cosine"},
            )
        return self._collections[collection_name]

    def add_items(
        self,
        ids: list[str],
        documents: list[str],
        metadatas: list[dict],
        embeddings: list[list[float]],
        collection_name: ZkCollectionName = ZkCollectionName.ZETTELKASTEN,
    ) -> None:
        """Upsert documents with their embeddings into the specified collection."""
        collection = self.get_collection(collection_name)
        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def delete_items(
        self,
        collection_name: ZkCollectionName,
        ids: list[str] | None = None,
        where: dict | None = None,
    ) -> None:
        """Remove documents from a collection by id list or metadata filter."""
        collection = self.get_collection(collection_name)
        collection.delete(ids=ids, where=where)

    def reset_indexes(self, collection_name: ZkCollectionName | None = None) -> None:
        """Drop and recreate the specified collection, or reset the entire database when ``None``."""
        if collection_name:
            try:
                self.chroma_client.delete_collection(collection_name.value)
            except ValueError:
                # Collection does not exist - this is fine
                pass
            self._collections.pop(collection_name, None)
            self.get_collection(collection_name)
        else:
            self.chroma_client.reset()
            self._collections = {}

    def query(
        self,
        query_embeddings: list[list[float]],
        n_results: int,
        collection_name: ZkCollectionName = ZkCollectionName.ZETTELKASTEN,
    ) -> dict:
        """Run a nearest-neighbour search and return the raw ChromaDB result dict."""
        collection = self.get_collection(collection_name)
        return collection.query(query_embeddings=query_embeddings, n_results=n_results)
