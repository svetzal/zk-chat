from unittest.mock import Mock

import pytest
import typer

from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.console_gateway import ConsoleGateway


class DescribeLoadConfigOrExit:
    """Tests for the load_config_or_exit helper function."""

    def should_return_config_when_config_is_present(self, tmp_path):
        from zk_chat.commands.config_helpers import load_config_or_exit

        mock_gateway = Mock(spec=ConfigGateway)
        mock_console_gateway = Mock(spec=ConsoleGateway)
        mock_config = Config(vault=str(tmp_path), model="test-model")
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


class DescribeResolveVaultOrExit:
    """Tests for the resolve_vault_or_exit helper function."""

    def should_return_vault_path_when_vault_arg_is_provided(
        self, tmp_path, mock_global_config_gateway, mock_console_gateway
    ):
        from zk_chat.commands.config_helpers import resolve_vault_or_exit

        result = resolve_vault_or_exit(
            tmp_path, mock_global_config_gateway, mock_console_gateway, "zk-chat test --vault /path"
        )

        assert result == str(tmp_path.resolve())

    def should_raise_exit_when_no_vault_and_no_bookmark(
        self, mock_global_config_gateway, mock_console_gateway
    ):
        from zk_chat.commands.config_helpers import resolve_vault_or_exit
        from zk_chat.global_config import GlobalConfig

        mock_global_config_gateway.load.return_value = GlobalConfig()

        with pytest.raises(typer.Exit):
            resolve_vault_or_exit(
                None, mock_global_config_gateway, mock_console_gateway, "zk-chat test --vault /path"
            )

    def should_print_command_hint_on_error(self, mock_global_config_gateway, mock_console_gateway):
        from zk_chat.commands.config_helpers import resolve_vault_or_exit
        from zk_chat.global_config import GlobalConfig

        mock_global_config_gateway.load.return_value = GlobalConfig()

        with pytest.raises(typer.Exit):
            resolve_vault_or_exit(
                None, mock_global_config_gateway, mock_console_gateway,
                "zk-chat index status --vault /path/to/vault"
            )

        calls = [str(call) for call in mock_console_gateway.print.call_args_list]
        assert any("zk-chat index status --vault /path/to/vault" in call for call in calls)


class DescribeResolveVaultAndLoadConfig:
    """Tests for the resolve_vault_and_load_config helper function."""

    def should_return_vault_path_and_config_on_success(
        self, tmp_path, mock_global_config_gateway, mock_config_gateway, mock_console_gateway
    ):
        from zk_chat.commands.config_helpers import resolve_vault_and_load_config

        expected_config = Config(vault=str(tmp_path), model="test-model")
        mock_config_gateway.load.return_value = expected_config

        vault_path, config = resolve_vault_and_load_config(
            tmp_path, mock_global_config_gateway, mock_config_gateway,
            mock_console_gateway, "zk-chat test --vault /path"
        )

        assert vault_path == str(tmp_path.resolve())
        assert config is expected_config

    def should_raise_exit_when_vault_resolution_fails(
        self, mock_global_config_gateway, mock_config_gateway, mock_console_gateway
    ):
        from zk_chat.commands.config_helpers import resolve_vault_and_load_config
        from zk_chat.global_config import GlobalConfig

        mock_global_config_gateway.load.return_value = GlobalConfig()

        with pytest.raises(typer.Exit):
            resolve_vault_and_load_config(
                None, mock_global_config_gateway, mock_config_gateway,
                mock_console_gateway, "zk-chat test --vault /path"
            )

    def should_raise_exit_when_config_load_fails(
        self, tmp_path, mock_global_config_gateway, mock_config_gateway, mock_console_gateway
    ):
        from zk_chat.commands.config_helpers import resolve_vault_and_load_config

        mock_config_gateway.load.return_value = None

        with pytest.raises(typer.Exit):
            resolve_vault_and_load_config(
                tmp_path, mock_global_config_gateway, mock_config_gateway,
                mock_console_gateway, "zk-chat test --vault /path"
            )


class DescribeShowHelpIfNoSubcommand:
    """Tests for the show_help_if_no_subcommand helper function."""

    def should_print_help_and_tips_when_no_subcommand(self, mock_console_gateway):
        from zk_chat.commands.config_helpers import show_help_if_no_subcommand

        ctx = Mock()
        ctx.invoked_subcommand = None
        ctx.obj = {"console_gateway": mock_console_gateway}
        ctx.get_help.return_value = "help text"

        show_help_if_no_subcommand(ctx, "tip line 1", "tip line 2")

        calls = [str(call) for call in mock_console_gateway.print.call_args_list]
        assert any("help text" in call for call in calls)
        assert any("tip line 1" in call for call in calls)
        assert any("tip line 2" in call for call in calls)

    def should_not_print_when_subcommand_is_invoked(self, mock_console_gateway):
        from zk_chat.commands.config_helpers import show_help_if_no_subcommand

        ctx = Mock()
        ctx.invoked_subcommand = "some_command"
        ctx.obj = {"console_gateway": mock_console_gateway}

        show_help_if_no_subcommand(ctx, "tip line 1")

        mock_console_gateway.print.assert_not_called()
