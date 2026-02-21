"""
Unit tests for the pure GlobalConfig data model.

GlobalConfig should be a plain Pydantic model — mutation methods should not
auto-save to disk. These tests verify pure data behaviour with no mocking needed.
"""

from zk_chat.global_config import GlobalConfig


class DescribeGlobalConfig:
    """Tests for the pure GlobalConfig data model."""

    def should_instantiate_with_empty_defaults(self):
        config = GlobalConfig()

        assert config.bookmarks == set()
        assert config.last_opened_bookmark is None
        assert config.mcp_servers == {}

    class DescribeAddBookmark:
        """Tests for add_bookmark() pure method."""

        def should_add_bookmark(self):
            config = GlobalConfig()

            config.add_bookmark("/my/vault")

            assert "/my/vault" in config.bookmarks

        def should_store_path_as_given(self):
            config = GlobalConfig()

            config.add_bookmark("/absolute/vault")

            assert "/absolute/vault" in config.bookmarks

        def should_add_multiple_bookmarks(self):
            config = GlobalConfig()

            config.add_bookmark("/vault/one")
            config.add_bookmark("/vault/two")

            assert "/vault/one" in config.bookmarks
            assert "/vault/two" in config.bookmarks

    class DescribeRemoveBookmark:
        """Tests for remove_bookmark() pure method."""

        def should_remove_existing_bookmark(self):
            config = GlobalConfig()
            config.bookmarks.add("/my/vault")

            result = config.remove_bookmark("/my/vault")

            assert result is True
            assert "/my/vault" not in config.bookmarks

        def should_return_false_when_removing_nonexistent_bookmark(self):
            config = GlobalConfig()

            result = config.remove_bookmark("/nonexistent")

            assert result is False

        def should_clear_last_opened_when_removing_its_bookmark(self):
            config = GlobalConfig()
            config.bookmarks.add("/my/vault")
            config.last_opened_bookmark = "/my/vault"

            config.remove_bookmark("/my/vault")

            assert config.last_opened_bookmark is None

        def should_not_clear_last_opened_when_removing_different_bookmark(self):
            config = GlobalConfig()
            config.bookmarks.add("/vault/one")
            config.bookmarks.add("/vault/two")
            config.last_opened_bookmark = "/vault/two"

            config.remove_bookmark("/vault/one")

            assert config.last_opened_bookmark == "/vault/two"

    class DescribeSetLastOpenedBookmark:
        """Tests for set_last_opened_bookmark() pure method."""

        def should_set_last_opened_bookmark(self):
            config = GlobalConfig()
            config.bookmarks.add("/my/vault")

            result = config.set_last_opened_bookmark("/my/vault")

            assert result is True
            assert config.last_opened_bookmark == "/my/vault"

        def should_return_false_when_setting_last_opened_to_non_bookmark(self):
            config = GlobalConfig()

            result = config.set_last_opened_bookmark("/not/bookmarked")

            assert result is False
            assert config.last_opened_bookmark is None

    class DescribeGetLastOpenedBookmarkPath:
        """Tests for get_last_opened_bookmark_path() pure method."""

        def should_return_last_opened_path(self):
            config = GlobalConfig()
            config.bookmarks.add("/my/vault")
            config.last_opened_bookmark = "/my/vault"

            result = config.get_last_opened_bookmark_path()

            assert result == "/my/vault"

        def should_return_none_when_no_last_opened(self):
            config = GlobalConfig()

            result = config.get_last_opened_bookmark_path()

            assert result is None

        def should_return_none_when_last_opened_not_in_bookmarks(self):
            config = GlobalConfig()
            config.last_opened_bookmark = "/removed/vault"

            result = config.get_last_opened_bookmark_path()

            assert result is None
