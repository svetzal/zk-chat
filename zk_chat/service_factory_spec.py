"""BDD-style tests for build_service_registry factory."""

from unittest.mock import Mock

import pytest
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway

from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_service import ConsoleGateway
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.service_factory import build_service_registry
from zk_chat.services.service_registry import ServiceType
from zk_chat.tools.git_gateway import GitGateway


@pytest.fixture
def config():
    return Config(vault="/test/vault", model="llama2", gateway=ModelGateway.OLLAMA)


@pytest.fixture
def mock_model_gateway():
    return Mock(spec=OllamaGateway)


@pytest.fixture
def mock_chroma_gateway():
    return Mock(spec=ChromaGateway)


@pytest.fixture
def registry(config, mock_model_gateway, mock_chroma_gateway):
    return build_service_registry(
        config=config,
        config_gateway=Mock(spec=ConfigGateway),
        global_config_gateway=Mock(spec=GlobalConfigGateway),
        model_gateway=mock_model_gateway,
        chroma_gateway=mock_chroma_gateway,
        filesystem_gateway=Mock(spec=MarkdownFilesystemGateway),
        tokenizer_gateway=Mock(spec=TokenizerGateway),
        git_gateway=Mock(spec=GitGateway),
        console_service=Mock(spec=ConsoleGateway),
    )


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

    def should_register_the_provided_model_gateway(self, config, mock_model_gateway, mock_chroma_gateway):
        registry = build_service_registry(
            config=config,
            config_gateway=Mock(spec=ConfigGateway),
            global_config_gateway=Mock(spec=GlobalConfigGateway),
            model_gateway=mock_model_gateway,
            chroma_gateway=mock_chroma_gateway,
            filesystem_gateway=Mock(spec=MarkdownFilesystemGateway),
            tokenizer_gateway=Mock(spec=TokenizerGateway),
            git_gateway=Mock(spec=GitGateway),
            console_service=Mock(spec=ConsoleGateway),
        )

        assert registry.get_service(ServiceType.MODEL_GATEWAY) is mock_model_gateway
