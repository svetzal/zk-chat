from unittest.mock import MagicMock, Mock

import pytest
import typer

from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_service import ConsoleGateway


class DescribeLoadConfigStatus:
    """Tests for the _load_config_status helper function."""

    def should_return_config_when_config_is_present(self, tmp_path):
        from zk_chat.commands.index import _load_config_status

        mock_gateway = Mock(spec=ConfigGateway)
        mock_console_gateway = Mock(spec=ConsoleGateway)
        mock_config = MagicMock()
        mock_gateway.load.return_value = mock_config

        result = _load_config_status(str(tmp_path), mock_gateway, mock_console_gateway)

        assert result is mock_config

    def should_raise_exit_when_config_is_none(self, tmp_path):
        from zk_chat.commands.index import _load_config_status

        mock_gateway = Mock(spec=ConfigGateway)
        mock_console_gateway = Mock(spec=ConsoleGateway)
        mock_gateway.load.return_value = None

        with pytest.raises(typer.Exit):
            _load_config_status(str(tmp_path), mock_gateway, mock_console_gateway)


class DescribePrintBasicConfig:
    """Tests for the _print_basic_config helper function."""

    def should_print_without_error(self):
        from zk_chat.commands.index import _print_basic_config
        from zk_chat.config import Config, ModelGateway

        config = Config(vault="/some/path", model="llama3", gateway=ModelGateway.OLLAMA)
        mock_console_gateway = Mock(spec=ConsoleGateway)

        _print_basic_config(config, mock_console_gateway)

        assert mock_console_gateway.print.called


class DescribePrintLastIndexed:
    """Tests for the _print_last_indexed helper function."""

    def should_print_last_indexed_when_previously_indexed(self):
        from datetime import datetime

        from zk_chat.commands.index import _print_last_indexed
        from zk_chat.config import Config, ModelGateway

        timestamp = datetime(2024, 1, 15, 12, 0, 0)
        config = Config(
            vault="/some/path",
            model="llama3",
            gateway=ModelGateway.OLLAMA,
            gateway_last_indexed={"ollama": timestamp},
        )
        mock_console_gateway = Mock(spec=ConsoleGateway)

        _print_last_indexed(config, mock_console_gateway)

        calls = [str(call) for call in mock_console_gateway.print.call_args_list]
        assert any("2024-01-15" in call for call in calls)

    def should_print_never_indexed_when_not_indexed(self):
        from zk_chat.commands.index import _print_last_indexed
        from zk_chat.config import Config, ModelGateway

        config = Config(vault="/some/path", model="llama3", gateway=ModelGateway.OLLAMA)
        mock_console_gateway = Mock(spec=ConsoleGateway)

        _print_last_indexed(config, mock_console_gateway)

        calls = [str(call) for call in mock_console_gateway.print.call_args_list]
        assert any("Never indexed" in call for call in calls)
