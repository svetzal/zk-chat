import hashlib
import os
from typing import List

import tiktoken

from chroma_gateway import ChromaGateway
from embedding_gateway import ollama_calculate_embedding
from markdown.loader import load_markdown
from models import ZkDocument, ZkDocumentChunk, ZkQueryResult
from rag.splitter import split_to_chunks


class Zettelkasten:
    def __init__(self, root_path: str, document_db: ChromaGateway):
        self.root_path = root_path
        self.document_db: ChromaGateway = document_db
        self.document_cache = None

    def all_markdown_documents(self) -> List[ZkDocument]:
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

    def read_zk_document(self, full_path: str) -> ZkDocument:
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
        return next((document for document in self.all_markdown_documents() if document.id == id), None)

    def chunk_and_index(self, chunk_size=200, chunk_overlap=20):
        self.document_db.reset_indexes()
        tokenizer = tiktoken.get_encoding("cl100k_base")
        documents = self.all_markdown_documents()
        for document in documents:
            self._chunk_document(tokenizer, document, chunk_size, chunk_overlap)

    def query_chunks(self, query: str, n_results: int = 5, max_distance: float = 1.0) -> List[ZkQueryResult]:
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
                results.append(ZkQueryResult(chunk=chunk, distance=distance))
        return results

    def _chunk_document(self, tokenizer, document, chunk_size=200, chunk_overlap=20):
        print(f"Processing {document.title}")
        tokens = tokenizer.encode(document.content)
        print(f"    Content is {len(document.content)} bytes, or {len(tokens)} tokens long")
        token_chunks = split_to_chunks(tokens, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if len(token_chunks) > 0:
            print(f"    Split into {len(token_chunks)} chunks")
            print([len(chunk) for chunk in token_chunks])

            text_chunks = self._decode_tokens_to_text(tokenizer, token_chunks)

            self._add_text_chunks_to_index(document, text_chunks)

    def _add_text_chunks_to_index(self, document, text_chunks):
        self.document_db.add_items(
            ids=[hashlib.md5(bytes(hunk, "utf-8")).hexdigest() for hunk in text_chunks],
            documents=text_chunks,
            metadatas=[{
                "id": document.id,
                "title": document.title,
            } for _ in text_chunks],
            embeddings=[self.tokenizer_gateway.encode(chunk) for chunk in text_chunks]
        )

    def _decode_tokens_to_text(self, tokenizer, token_chunks):
        return [tokenizer.decode(chunk) for chunk in token_chunks]
