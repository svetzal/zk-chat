"""BDD-style tests for create_model_gateway factory."""
from unittest.mock import Mock, patch

import pytest

from zk_chat.config import ModelGateway
from zk_chat.gateway_factory import create_model_gateway


class DescribeCreateModelGateway:
    def should_create_ollama_gateway_when_gateway_is_ollama(self):
        with patch("zk_chat.gateway_factory.OllamaGateway") as mock_ollama:
            mock_instance = Mock()
            mock_ollama.return_value = mock_instance

            result = create_model_gateway(ModelGateway.OLLAMA)

            mock_ollama.assert_called_once_with()
            assert result is mock_instance

    def should_create_openai_gateway_when_gateway_is_openai(self):
        with (
            patch("zk_chat.gateway_factory.OpenAIGateway") as mock_openai,
            patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}),
        ):
            mock_instance = Mock()
            mock_openai.return_value = mock_instance

            result = create_model_gateway(ModelGateway.OPENAI)

            mock_openai.assert_called_once_with("test-key")
            assert result is mock_instance

    def should_pass_api_key_from_environment_to_openai_gateway(self):
        with (
            patch("zk_chat.gateway_factory.OpenAIGateway") as mock_openai,
            patch.dict("os.environ", {"OPENAI_API_KEY": "my-api-key"}),
        ):
            create_model_gateway(ModelGateway.OPENAI)

            mock_openai.assert_called_once_with("my-api-key")

    def should_raise_value_error_for_unrecognized_gateway(self):
        with pytest.raises(ValueError, match="Unsupported gateway type"):
            create_model_gateway("unsupported")  # type: ignore[arg-type]
