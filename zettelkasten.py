import hashlib
import os
import re
from typing import List

import tiktoken
from pydantic import BaseModel

from chroma_gateway import ChromaGateway
from markdown import load_markdown
from embedding_gateway import ollama_calculate_embedding
from rag import split_to_chunks


class ZkDocument(BaseModel):
    relative_path: str
    metadata: dict
    content: str

    @property
    def title(self) -> str:
        return self.strip_identifier_prefix(self.base_filename_without_extension())

    @property
    def id(self) -> str:
        return self.relative_path

    def strip_identifier_prefix(self, string):
        return re.sub(r'^[@!]\s*', '', string)

    def base_filename_without_extension(self):
        return os.path.splitext(os.path.basename(self.relative_path))[0]


class ZkDocumentChunk(BaseModel):
    document_id: str
    document_title: str
    text: str


class QueryResult(BaseModel):
    chunk: ZkDocumentChunk
    distance: float


class Zettelkasten:
    def __init__(self, root_path: str, document_db: ChromaGateway):
        self.root_path = root_path
        self.document_db: ChromaGateway = document_db
        self.document_cache = None

    def all_documents(self) -> List[ZkDocument]:
        if not self.document_cache:
            documents = []
            for dirpath, _, filenames in os.walk(self.root_path):
                for filename in filenames:
                    if filename.endswith(".md"):
                        full_path = os.path.join(dirpath, filename)
                        document = self.read_zk_document(full_path)
                        documents.append(document)
            self.document_cache = documents
        return self.document_cache

    def read_zk_document(self, full_path):
        relative_path = os.path.relpath(full_path, self.root_path)
        (metadata, content) = load_markdown(full_path)
        document = ZkDocument(
            relative_path=relative_path,
            metadata=metadata,
            content=content
        )
        return document

    # How long will it be feasible to just load this all into RAM?
    def find_by_id(self, id: str) -> ZkDocument:
        return next((document for document in self.all_documents() if document.id == id), None)

    def chunk_and_index(self, chunk_size=200, chunk_overlap=20):
        self.document_db.reset_indexes()
        tokenizer = tiktoken.get_encoding("cl100k_base")
        documents = self.all_documents()
        for document in documents:
            print(f"Processing {document.title}")
            tokens = tokenizer.encode(document.content)

            print(f"    Content is {len(document.content)} bytes, or {len(tokens)} tokens long")

            token_chunks = split_to_chunks(tokens, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

            if len(token_chunks) > 0:
                print(f"    Split into {len(token_chunks)} chunks")
                print([len(chunk) for chunk in token_chunks])

                text_chunks = [tokenizer.decode(chunk) for chunk in token_chunks]

                self.document_db.add_items(
                    ids=[hashlib.md5(bytes(hunk, "utf-8")).hexdigest() for hunk in text_chunks],
                    documents=text_chunks,
                    metadatas=[{
                        "id": document.id,
                        "title": document.title,
                    } for _ in text_chunks],
                    embeddings=[ollama_calculate_embedding(chunk) for chunk in text_chunks]
                )

    def query_chunks(self, query: str, n_results: int = 5, max_distance: float = 1.0) -> List[QueryResult]:
        query_embedding = ollama_calculate_embedding(query)
        response = self.document_db.query(query_embedding, n_results=n_results)
        # print(response.keys()) # ids, embeddings, documents, uris, data, metadata, distances, included
        results = []
        for i, distance in enumerate(response['distances'][0]):
            if distance <= max_distance:
                chunk = ZkDocumentChunk(
                    document_id=response['metadatas'][0][i]['id'],
                    document_title=response['metadatas'][0][i]['title'],
                    text=response['documents'][0][i]
                )
                results.append(QueryResult(chunk=chunk, distance=distance))
        return results
