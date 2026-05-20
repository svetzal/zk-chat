"""
Integration tests for GlobalConfigGateway.

These tests exercise real file I/O using a temporary file — this is correct
for gateway tests, which should verify actual I/O behaviour rather than mocking it.
"""

import pytest
import structlog.testing

from zk_chat.global_config import GlobalConfig, MCPServerConfig, MCPServerType
from zk_chat.global_config_gateway import GlobalConfigGateway


@pytest.fixture
def tmp_config_path(tmp_path):
    """Provide a temporary path for the global config file."""
    return str(tmp_path / ".zk_chat")


@pytest.fixture
def global_config_gateway(tmp_config_path):
    """Provide a GlobalConfigGateway with an injected temp path."""
    return GlobalConfigGateway(config_path=tmp_config_path)


class DescribeGlobalConfigGateway:
    """Tests for GlobalConfigGateway — global config persistence."""

    def should_return_default_config_when_no_file_exists(self, global_config_gateway):
        result = global_config_gateway.load()

        assert isinstance(result, GlobalConfig)
        assert result.bookmarks == set()
        assert result.last_opened_bookmark is None
        assert result.mcp_servers == {}

    def should_load_config_from_existing_file(self, global_config_gateway, tmp_config_path):
        config = GlobalConfig()
        config.bookmarks.add("/some/vault")
        config.last_opened_bookmark = "/some/vault"
        global_config_gateway.save(config)

        result = global_config_gateway.load()

        assert "/some/vault" in result.bookmarks
        assert result.last_opened_bookmark == "/some/vault"

    def should_save_config_to_file(self, global_config_gateway, tmp_config_path):
        import os

        config = GlobalConfig()

        global_config_gateway.save(config)

        assert os.path.exists(tmp_config_path)

    def should_return_default_config_when_file_is_corrupt(self, global_config_gateway, tmp_config_path):
        with open(tmp_config_path, "w") as f:
            f.write("not valid json {{{")

        result = global_config_gateway.load()

        assert isinstance(result, GlobalConfig)
        assert result.bookmarks == set()

    def should_log_warning_when_file_contains_malformed_json(self, global_config_gateway, tmp_config_path):
        with open(tmp_config_path, "w") as f:
            f.write("not valid json {{{")

        with structlog.testing.capture_logs() as cap_logs:
            global_config_gateway.load()

        warning_logs = [entry for entry in cap_logs if entry.get("log_level") == "warning"]
        assert len(warning_logs) == 1
        assert "Corrupt" in warning_logs[0]["event"]

    def should_log_warning_when_file_has_wrong_types(self, global_config_gateway, tmp_config_path):
        with open(tmp_config_path, "w") as f:
            f.write('{"bookmarks": "not-a-set", "last_opened_bookmark": 12345}')

        with structlog.testing.capture_logs() as cap_logs:
            result = global_config_gateway.load()

        assert isinstance(result, GlobalConfig)
        warning_logs = [entry for entry in cap_logs if entry.get("log_level") == "warning"]
        assert len(warning_logs) == 1

    def should_round_trip_config_through_save_and_load(self, global_config_gateway):
        server = MCPServerConfig(
            name="test-server",
            server_type=MCPServerType.STDIO,
            command="my-command",
            args=["--flag"],
        )
        original = GlobalConfig()
        original.bookmarks.add("/my/vault")
        original.last_opened_bookmark = "/my/vault"
        original.mcp_servers["test-server"] = server

        global_config_gateway.save(original)
        loaded = global_config_gateway.load()

        assert "/my/vault" in loaded.bookmarks
        assert loaded.last_opened_bookmark == "/my/vault"
        assert "test-server" in loaded.mcp_servers
        assert loaded.mcp_servers["test-server"].command == "my-command"

    def should_overwrite_existing_config_on_save(self, global_config_gateway):
        first = GlobalConfig()
        first.bookmarks.add("/first/vault")
        global_config_gateway.save(first)

        second = GlobalConfig()
        second.bookmarks.add("/second/vault")
        global_config_gateway.save(second)
        loaded = global_config_gateway.load()

        assert "/first/vault" not in loaded.bookmarks
        assert "/second/vault" in loaded.bookmarks
