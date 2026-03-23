"""
Tests for bookmarks command helper functions.
"""

from unittest.mock import Mock

import pytest

from zk_chat.commands.bookmarks import _list_bookmarks, _remove_bookmark
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway


@pytest.fixture
def mock_gateway():
    return Mock(spec=GlobalConfigGateway)


class DescribeListBookmarks:
    """Tests for the _list_bookmarks helper function."""

    def should_load_config_from_gateway(self, mock_gateway):
        mock_gateway.load.return_value = GlobalConfig()

        _list_bookmarks(mock_gateway)

        mock_gateway.load.assert_called_once()

    def should_handle_empty_bookmarks(self, mock_gateway):
        mock_gateway.load.return_value = GlobalConfig()

        _list_bookmarks(mock_gateway)

        mock_gateway.load.assert_called_once()


class DescribeRemoveBookmark:
    """Tests for the _remove_bookmark helper function."""

    def should_return_true_when_bookmark_exists(self, mock_gateway):
        config = GlobalConfig()
        import os

        abs_path = os.path.abspath("/some/vault")
        config.add_bookmark(abs_path)
        mock_gateway.load.return_value = config

        result = _remove_bookmark(abs_path, mock_gateway)

        assert result is True
        mock_gateway.save.assert_called_once()

    def should_return_false_when_bookmark_not_found(self, mock_gateway):
        mock_gateway.load.return_value = GlobalConfig()

        result = _remove_bookmark("/nonexistent/path", mock_gateway)

        assert result is False
        mock_gateway.save.assert_not_called()

    def should_use_gateway_to_save_after_removal(self, mock_gateway):
        config = GlobalConfig()
        import os

        abs_path = os.path.abspath("/vault/path")
        config.add_bookmark(abs_path)
        mock_gateway.load.return_value = config

        _remove_bookmark(abs_path, mock_gateway)

        mock_gateway.save.assert_called_once_with(config)
