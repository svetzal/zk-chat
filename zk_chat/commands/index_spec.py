from unittest.mock import MagicMock, Mock, patch

import pytest
import typer

from zk_chat.config_gateway import ConfigGateway
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway


class DescribeResolveVaultStatus:
    """Tests for the _resolve_vault_status helper function."""

    def should_return_resolved_path_when_vault_provided(self, tmp_path):
        from zk_chat.commands.index import _resolve_vault_status

        mock_gateway = Mock(spec=GlobalConfigGateway)

        result = _resolve_vault_status(tmp_path, mock_gateway)

        assert result == str(tmp_path.resolve())

    def should_load_global_config_when_vault_is_none(self, tmp_path):
        from zk_chat.commands.index import _resolve_vault_status

        mock_gateway = Mock(spec=GlobalConfigGateway)
        global_config = GlobalConfig()
        global_config.add_bookmark(str(tmp_path))
        global_config.set_last_opened_bookmark(str(tmp_path))
        mock_gateway.load.return_value = global_config

        result = _resolve_vault_status(None, mock_gateway)

        assert result == str(tmp_path)

    def should_raise_exit_when_no_bookmarks_and_vault_is_none(self):
        from zk_chat.commands.index import _resolve_vault_status

        mock_gateway = Mock(spec=GlobalConfigGateway)
        empty_config = GlobalConfig()
        mock_gateway.load.return_value = empty_config

        with patch("zk_chat.commands.index.console"):
            with pytest.raises(typer.Exit):
                _resolve_vault_status(None, mock_gateway)

    def should_raise_exit_when_vault_path_does_not_exist(self, tmp_path):
        from zk_chat.commands.index import _resolve_vault_status

        non_existent = tmp_path / "does_not_exist"
        mock_gateway = Mock(spec=GlobalConfigGateway)

        with patch("zk_chat.commands.index.console"):
            with pytest.raises(typer.Exit):
                _resolve_vault_status(non_existent, mock_gateway)


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


class DescribeCountMarkdownFiles:
    """Tests for the _count_markdown_files helper function."""

    def should_count_markdown_files_in_directory(self, tmp_path):
        from zk_chat.commands.index import _count_markdown_files

        (tmp_path / "note1.md").write_text("content")
        (tmp_path / "note2.md").write_text("content")
        (tmp_path / "image.png").write_text("not markdown")

        result = _count_markdown_files(str(tmp_path))

        assert result == 2

    def should_count_markdown_files_recursively(self, tmp_path):
        from zk_chat.commands.index import _count_markdown_files

        (tmp_path / "note1.md").write_text("content")
        subdir = tmp_path / "subdir"
        subdir.mkdir()
        (subdir / "note2.md").write_text("content")

        result = _count_markdown_files(str(tmp_path))

        assert result == 2

    def should_skip_zk_chat_db_directory(self, tmp_path):
        from zk_chat.commands.index import _count_markdown_files

        (tmp_path / "note1.md").write_text("content")
        db_dir = tmp_path / ".zk_chat_db"
        db_dir.mkdir()
        (db_dir / "internal.md").write_text("internal")

        result = _count_markdown_files(str(tmp_path))

        assert result == 1

    def should_return_zero_when_no_markdown_files(self, tmp_path):
        from zk_chat.commands.index import _count_markdown_files

        (tmp_path / "document.txt").write_text("content")

        result = _count_markdown_files(str(tmp_path))

        assert result == 0


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
