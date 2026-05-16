from unittest.mock import MagicMock, Mock

import pytest
import typer

from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_gateway import ConsoleGateway


class DescribeLoadConfigOrExit:
    """Tests for the load_config_or_exit helper function."""

    def should_return_config_when_config_is_present(self, tmp_path):
        from zk_chat.commands.config_helpers import load_config_or_exit

        mock_gateway = Mock(spec=ConfigGateway)
        mock_console_gateway = Mock(spec=ConsoleGateway)
        mock_config = MagicMock()
        mock_gateway.load.return_value = mock_config

        result = load_config_or_exit(str(tmp_path), mock_gateway, mock_console_gateway)

        assert result is mock_config

    def should_raise_exit_when_config_is_none(self, tmp_path):
        from zk_chat.commands.config_helpers import load_config_or_exit

        mock_gateway = Mock(spec=ConfigGateway)
        mock_console_gateway = Mock(spec=ConsoleGateway)
        mock_gateway.load.return_value = None

        with pytest.raises(typer.Exit):
            load_config_or_exit(str(tmp_path), mock_gateway, mock_console_gateway)
