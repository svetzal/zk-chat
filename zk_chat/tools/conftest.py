from unittest.mock import Mock

import pytest
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.index_service import IndexService
from zk_chat.vector_database import VectorDatabase


def _make_index_service(chroma_excerpts=None, chroma_documents=None, filesystem=None):
    """Build a real IndexService with gateway mocks."""
    gateway = Mock(spec=OllamaGateway)
    gateway.calculate_embeddings.return_value = [0.1, 0.2, 0.3]

    if chroma_excerpts is None:
        chroma_excerpts = Mock(spec=ChromaGateway)
    if chroma_documents is None:
        chroma_documents = Mock(spec=ChromaGateway)
    if filesystem is None:
        filesystem = Mock(spec=MarkdownFilesystemGateway)

    return IndexService(
        tokenizer_gateway=Mock(spec=TokenizerGateway),
        excerpts_db=VectorDatabase(chroma_excerpts, gateway, ZkCollectionName.EXCERPTS),
        documents_db=VectorDatabase(chroma_documents, gateway, ZkCollectionName.DOCUMENTS),
        filesystem_gateway=filesystem,
    )


@pytest.fixture
def make_index_service():
    """Pytest fixture that returns the _make_index_service factory function."""
    return _make_index_service
