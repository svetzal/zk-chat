"""BDD-style tests for build_service_registry factory."""
from unittest.mock import Mock, patch

import pytest

from zk_chat.config import Config, ModelGateway
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_registry import ServiceType


@pytest.fixture
def config():
    return Config(vault="/test/vault", model="llama2", gateway=ModelGateway.OLLAMA)


@pytest.fixture
def registry(config):
    with (
        patch("zk_chat.service_factory.create_model_gateway") as mock_create_gateway,
        patch("zk_chat.service_factory.ChromaGateway") as mock_chroma,
        patch("zk_chat.service_factory.VectorDatabase") as mock_vdb,
    ):
        mock_create_gateway.return_value = Mock()
        mock_chroma.return_value = Mock()
        mock_vdb.return_value = Mock()
        return build_service_registry(config)


class DescribeBuildServiceRegistry:
    def should_register_config(self, config, registry):
        assert registry.has_service(ServiceType.CONFIG)
        assert registry.get_service(ServiceType.CONFIG) is config

    def should_register_model_gateway(self, registry):
        assert registry.has_service(ServiceType.MODEL_GATEWAY)

    def should_register_chroma_gateway(self, registry):
        assert registry.has_service(ServiceType.CHROMA_GATEWAY)

    def should_register_filesystem_gateway(self, registry):
        assert registry.has_service(ServiceType.FILESYSTEM_GATEWAY)

    def should_register_tokenizer_gateway(self, registry):
        assert registry.has_service(ServiceType.TOKENIZER_GATEWAY)

    def should_register_document_service(self, registry):
        assert registry.has_service(ServiceType.DOCUMENT_SERVICE)

    def should_register_index_service(self, registry):
        assert registry.has_service(ServiceType.INDEX_SERVICE)

    def should_register_link_traversal_service(self, registry):
        assert registry.has_service(ServiceType.LINK_TRAVERSAL_SERVICE)

    def should_register_llm_broker(self, registry):
        assert registry.has_service(ServiceType.LLM_BROKER)

    def should_register_smart_memory(self, registry):
        assert registry.has_service(ServiceType.SMART_MEMORY)

    def should_register_git_gateway(self, registry):
        assert registry.has_service(ServiceType.GIT_GATEWAY)

    def should_use_create_model_gateway_with_configured_gateway(self, config):
        with (
            patch("zk_chat.service_factory.create_model_gateway") as mock_create_gateway,
            patch("zk_chat.service_factory.ChromaGateway"),
            patch("zk_chat.service_factory.VectorDatabase"),
        ):
            mock_create_gateway.return_value = Mock()

            build_service_registry(config)

            mock_create_gateway.assert_called_once_with(config.gateway)
