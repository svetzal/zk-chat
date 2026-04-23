"""Tests for vault path resolution."""

from pathlib import Path
from unittest.mock import Mock

import pytest

from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.vault_resolution import VaultResolutionError, resolve_vault_path


class DescribeResolveVaultPath:
    """Tests for the resolve_vault_path pure function."""

    def should_return_resolved_path_when_vault_explicitly_provided(self, tmp_path):
        mock_gateway = Mock(spec=GlobalConfigGateway)

        result = resolve_vault_path(tmp_path, mock_gateway)

        assert result == str(tmp_path.resolve())

    def should_not_call_gateway_when_vault_explicitly_provided(self, tmp_path):
        mock_gateway = Mock(spec=GlobalConfigGateway)

        resolve_vault_path(tmp_path, mock_gateway)

        mock_gateway.load.assert_not_called()

    def should_resolve_path_from_bookmarks_when_no_vault_provided(self, tmp_path):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_config = Mock(spec=GlobalConfig)
        mock_config.get_last_opened_bookmark_path.return_value = str(tmp_path)
        mock_gateway.load.return_value = mock_config

        result = resolve_vault_path(None, mock_gateway)

        assert result == str(tmp_path)

    def should_raise_error_when_no_vault_and_no_bookmarks(self):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_config = Mock(spec=GlobalConfig)
        mock_config.get_last_opened_bookmark_path.return_value = None
        mock_gateway.load.return_value = mock_config

        with pytest.raises(VaultResolutionError) as exc_info:
            resolve_vault_path(None, mock_gateway)

        assert "No vault specified and no bookmarks found" in str(exc_info.value)

    def should_raise_error_when_explicit_path_does_not_exist(self):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        non_existent = Path("/nonexistent/path/that/does/not/exist")

        with pytest.raises(VaultResolutionError) as exc_info:
            resolve_vault_path(non_existent, mock_gateway)

        assert "does not exist" in str(exc_info.value)

    def should_raise_error_when_bookmarked_path_does_not_exist(self):
        mock_gateway = Mock(spec=GlobalConfigGateway)
        mock_config = Mock(spec=GlobalConfig)
        mock_config.get_last_opened_bookmark_path.return_value = "/nonexistent/bookmarked/path"
        mock_gateway.load.return_value = mock_config

        with pytest.raises(VaultResolutionError) as exc_info:
            resolve_vault_path(None, mock_gateway)

        assert "does not exist" in str(exc_info.value)
