from unittest.mock import MagicMock, Mock, patch

import pytest
import typer

from zk_chat.config_gateway import ConfigGateway


class DescribeLoadConfigStatus:
    """Tests for the _load_config_status helper function."""

    def should_return_config_when_config_is_present(self, tmp_path):
        from zk_chat.commands.index import _load_config_status

        mock_gateway = Mock(spec=ConfigGateway)
        mock_config = MagicMock()
        mock_gateway.load.return_value = mock_config

        result = _load_config_status(str(tmp_path), mock_gateway)

        assert result is mock_config

    def should_raise_exit_when_config_is_none(self, tmp_path):
        from zk_chat.commands.index import _load_config_status

        mock_gateway = Mock(spec=ConfigGateway)
        mock_gateway.load.return_value = None

        with patch("zk_chat.commands.index.console"):
            with pytest.raises(typer.Exit):
                _load_config_status(str(tmp_path), mock_gateway)


class DescribePrintBasicConfig:
    """Tests for the _print_basic_config helper function."""

    def should_print_without_error(self):
        from zk_chat.commands.index import _print_basic_config
        from zk_chat.config import Config, ModelGateway

        config = Config(vault="/some/path", model="llama3", gateway=ModelGateway.OLLAMA)

        with patch("zk_chat.commands.index.console") as mock_console:
            _print_basic_config(config)

        assert mock_console.print.called


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

        with patch("zk_chat.commands.index.console") as mock_console:
            _print_last_indexed(config)

        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("2024-01-15" in call for call in calls)

    def should_print_never_indexed_when_not_indexed(self):
        from zk_chat.commands.index import _print_last_indexed
        from zk_chat.config import Config, ModelGateway

        config = Config(vault="/some/path", model="llama3", gateway=ModelGateway.OLLAMA)

        with patch("zk_chat.commands.index.console") as mock_console:
            _print_last_indexed(config)

        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("Never indexed" in call for call in calls)
