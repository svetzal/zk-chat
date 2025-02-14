import hashlib
import os
from typing import List

from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.markdown.loader import load_markdown
from zk_chat.models import ZkDocument, ZkDocumentChunk, ZkQueryResult
from zk_chat.rag.splitter import split_to_chunks


class Zettelkasten:
    def __init__(self, root_path: str, embeddings_gateway: EmbeddingsGateway, tokenizer_gateway: TokenizerGateway,
                 document_db: ChromaGateway):
        self.root_path = root_path
        self.embeddings_gateway: EmbeddingsGateway = embeddings_gateway
        self.tokenizer_gateway: TokenizerGateway = tokenizer_gateway
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
        documents = self.all_markdown_documents()
        for document in documents:
            self._chunk_document(document, chunk_size, chunk_overlap)

    def query_chunks(self, query: str, n_results: int = 5, max_distance: float = 1.0) -> List[ZkQueryResult]:
        query_embedding = self.embeddings_gateway.calculate(query)
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

    def _chunk_document(self, document, chunk_size=200, chunk_overlap=20):
        print(f"Processing {document.title}")
        tokens = self.tokenizer_gateway.encode(document.content)
        print(f"    Content is {len(document.content)} bytes, or {len(tokens)} tokens long")
        token_chunks = split_to_chunks(tokens, chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        if len(token_chunks) > 0:
            print(f"    Split into {len(token_chunks)} chunks")
            print([len(chunk) for chunk in token_chunks])

            text_chunks = self._decode_tokens_to_text(token_chunks)

            self._add_text_chunks_to_index(document, text_chunks)

    def _add_text_chunks_to_index(self, document, text_chunks):
        self.document_db.add_items(
            ids=[hashlib.md5(bytes(hunk, "utf-8")).hexdigest() for hunk in text_chunks],
            documents=text_chunks,
            metadatas=[{
                "id": document.id,
                "title": document.title,
            } for _ in text_chunks],
            embeddings=[self.embeddings_gateway.calculate(chunk) for chunk in text_chunks]
        )

    def _decode_tokens_to_text(self, token_chunks):
        return [self.tokenizer_gateway.decode(chunk) for chunk in token_chunks]
