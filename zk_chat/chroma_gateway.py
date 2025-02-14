import os

import chromadb
from chromadb import Settings


class ChromaGateway:
    def __init__(self, partition_name: str = "zettelkasten", db_dir: str = None):
        # Set default db directory if not provided
        if db_dir is None:
            db_dir = os.path.expanduser("~/.zk_chat_db/")
        self.partition_name = partition_name
        # Update Settings with persist_directory
        self.chroma_client = chromadb.PersistentClient(
            path=db_dir,
            settings=Settings(allow_reset=True),
        )
        self.collection = self.init_collection()

    def init_collection(self):
        return self.chroma_client.get_or_create_collection(
            name=self.partition_name)  # , embedding_function=OllamaEmbeddingFunction())

    def add_items(self, ids, documents, metadatas, embeddings):
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

    def reset_indexes(self):
        self.chroma_client.reset()
        self.collection = self.init_collection()

    def query(self, query_embeddings, n_results):
        return self.collection.query(query_embeddings=query_embeddings, n_results=n_results)
