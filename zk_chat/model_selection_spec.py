from unittest.mock import Mock, patch

import pytest

from zk_chat.config import ModelGateway
from zk_chat.console_gateway import ConsoleGateway
from zk_chat.model_selection import get_available_models, select_model


@pytest.fixture
def mock_console():
    return Mock(spec=ConsoleGateway)


class DescribeSelectModel:
    """Tests for select_model() interactive branching over ConsoleGateway."""

    def should_return_chosen_model_on_valid_numeric_input(self, mock_console):
        models = ["llama3.2", "mistral", "gemma2"]
        mock_console.input.return_value = "2"

        with patch("zk_chat.model_selection.get_available_models", return_value=models):
            result = select_model(ModelGateway.OLLAMA, console_gateway=mock_console)

        assert result == "mistral"

    def should_reprompt_on_non_numeric_input_then_succeed(self, mock_console):
        models = ["llama3.2", "mistral"]
        mock_console.input.side_effect = ["abc", "1"]

        with patch("zk_chat.model_selection.get_available_models", return_value=models):
            result = select_model(ModelGateway.OLLAMA, console_gateway=mock_console)

        assert result == "llama3.2"
        invalid_calls = [
            c for c in mock_console.print.call_args_list if "Invalid selection" in str(c)
        ]
        assert len(invalid_calls) == 1

    def should_reprompt_on_out_of_bounds_low_then_succeed(self, mock_console):
        models = ["llama3.2", "mistral"]
        mock_console.input.side_effect = ["0", "1"]

        with patch("zk_chat.model_selection.get_available_models", return_value=models):
            result = select_model(ModelGateway.OLLAMA, console_gateway=mock_console)

        assert result == "llama3.2"
        invalid_calls = [
            c for c in mock_console.print.call_args_list if "Invalid selection" in str(c)
        ]
        assert len(invalid_calls) == 1

    def should_reprompt_on_out_of_bounds_high_then_succeed(self, mock_console):
        models = ["llama3.2", "mistral"]
        mock_console.input.side_effect = ["99", "2"]

        with patch("zk_chat.model_selection.get_available_models", return_value=models):
            result = select_model(ModelGateway.OLLAMA, console_gateway=mock_console)

        assert result == "mistral"
        invalid_calls = [
            c for c in mock_console.print.call_args_list if "Invalid selection" in str(c)
        ]
        assert len(invalid_calls) == 1

    def should_prompt_manual_entry_with_ollama_wording_when_no_models(self, mock_console):
        mock_console.input.return_value = "my-custom-model"

        with patch("zk_chat.model_selection.get_available_models", return_value=[]):
            result = select_model(ModelGateway.OLLAMA, console_gateway=mock_console)

        assert result == "my-custom-model"
        prompt_text = mock_console.input.call_args[0][0]
        assert "Ollama" in prompt_text

    def should_prompt_manual_entry_with_generic_wording_for_openai_no_models(self, mock_console):
        mock_console.input.return_value = "gpt-4o"

        with patch("zk_chat.model_selection.get_available_models", return_value=[]):
            result = select_model(ModelGateway.OPENAI, console_gateway=mock_console)

        assert result == "gpt-4o"
        prompt_text = mock_console.input.call_args[0][0]
        assert "Ollama" not in prompt_text


class DescribeGetAvailableModels:
    """Tests for get_available_models() error branches."""

    def should_return_empty_list_and_print_error_when_openai_key_missing(self, mock_console, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        result = get_available_models(ModelGateway.OPENAI, mock_console)

        assert result == []
        mock_console.print.assert_called_once()
        printed = str(mock_console.print.call_args[0][0])
        assert "OPENAI_API_KEY" in printed

    def should_return_empty_list_and_print_error_when_gateway_raises_value_error(self, mock_console, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")

        with patch("zk_chat.gateway_factory.create_model_gateway", side_effect=ValueError("bad config")):
            result = get_available_models(ModelGateway.OPENAI, mock_console)

        assert result == []
        mock_console.print.assert_called_once()
        printed = str(mock_console.print.call_args[0][0])
        assert "Error" in printed

    def should_return_model_list_on_success(self, mock_console, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_gateway = Mock()
        mock_gateway.get_available_models.return_value = ["gpt-4o", "gpt-4-turbo"]

        with patch("zk_chat.gateway_factory.create_model_gateway", return_value=mock_gateway):
            result = get_available_models(ModelGateway.OPENAI, mock_console)

        assert result == ["gpt-4o", "gpt-4-turbo"]
        mock_console.print.assert_not_called()
