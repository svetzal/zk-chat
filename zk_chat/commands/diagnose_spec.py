"""
Tests for diagnose command helper functions.
"""

from unittest.mock import Mock

import pytest
from click.exceptions import Exit as ClickExit

from zk_chat.commands.diagnose import _resolve_vault_path
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway


@pytest.fixture
def mock_gateway():
    return Mock(spec=GlobalConfigGateway)


class DescribeResolveVaultPath:
    """Tests for the _resolve_vault_path helper function."""

    def should_return_resolved_path_when_vault_provided(self, tmp_path):
        result = _resolve_vault_path(tmp_path)

        assert result == str(tmp_path.resolve())

    def should_use_gateway_to_load_config_when_no_vault(self, mock_gateway):
        config = GlobalConfig()
        mock_gateway.load.return_value = config

        with pytest.raises(ClickExit):
            _resolve_vault_path(None, mock_gateway)

        mock_gateway.load.assert_called_once()

    def should_raise_exit_when_no_vault_and_no_bookmarks(self, mock_gateway):
        mock_gateway.load.return_value = GlobalConfig()

        with pytest.raises(ClickExit):
            _resolve_vault_path(None, mock_gateway)

    def should_return_last_opened_bookmark_when_no_vault_arg(self, mock_gateway, tmp_path):
        config = GlobalConfig()
        config.add_bookmark(str(tmp_path))
        config.set_last_opened_bookmark(str(tmp_path))
        mock_gateway.load.return_value = config

        result = _resolve_vault_path(None, mock_gateway)

        assert result == str(tmp_path)
