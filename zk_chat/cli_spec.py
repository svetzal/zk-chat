from unittest.mock import Mock, patch

import pytest

from zk_chat.cli import _handle_save, _resolve_vault_path, common_init
from zk_chat.config import Config, ModelGateway
from zk_chat.config_resolution import GatewayValidationResult
from zk_chat.console_gateway import ConsoleGateway
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.init_options import InitOptions
from zk_chat.vault_path import normalize_vault_path


@pytest.fixture
def mock_global_config_gateway():
    gateway = Mock(spec=GlobalConfigGateway)
    gateway.load.return_value = GlobalConfig()
    return gateway


@pytest.fixture
def existing_config(tmp_path):
    return Config(vault=str(tmp_path), model="llama3", gateway=ModelGateway.OLLAMA)


class DescribeCommonInit:
    """Tests for the common_init orchestration function."""

    class DescribeWithSaveOption:
        def should_return_none_when_save_set_without_vault(
            self, mock_global_config_gateway, mock_config_gateway, mock_console_gateway
        ):
            options = InitOptions(save=True, vault=None)

            result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is None

        def should_print_error_when_save_set_without_vault(
            self, mock_global_config_gateway, mock_config_gateway, mock_console_gateway
        ):
            options = InitOptions(save=True, vault=None)

            common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            mock_console_gateway.print.assert_called_once_with("Error: --save requires --vault to be specified.")

        def should_return_none_when_save_set_with_nonexistent_vault(
            self, mock_global_config_gateway, mock_config_gateway, mock_console_gateway
        ):
            options = InitOptions(save=True, vault="/no/such/path")

            result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is None

        def should_return_none_and_save_bookmark_when_vault_exists(
            self, mock_global_config_gateway, mock_config_gateway, mock_console_gateway, tmp_path
        ):
            global_config = GlobalConfig()
            mock_global_config_gateway.load.return_value = global_config
            options = InitOptions(save=True, vault=str(tmp_path))

            result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is None
            mock_global_config_gateway.save.assert_called_once_with(global_config)

    class DescribeWithNoVaultAvailable:
        def should_return_none_when_no_vault_and_no_bookmarks(
            self, mock_global_config_gateway, mock_config_gateway, mock_console_gateway
        ):
            options = InitOptions()

            result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is None

    class DescribeWithExistingConfig:
        def should_return_config_when_vault_exists_with_config(
            self,
            mock_global_config_gateway,
            mock_config_gateway,
            mock_console_gateway,
            existing_config,
            tmp_path,
        ):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = existing_config
            options = InitOptions(reindex=False)

            with patch("zk_chat.cli._run_upgraders"), patch("zk_chat.cli.validate_gateway_selection") as mock_validate:
                mock_validate.return_value = GatewayValidationResult(
                    gateway=ModelGateway.OLLAMA, changed=False, error=None
                )

                result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is existing_config

        def should_return_none_when_reset_memory_is_true(
            self,
            mock_global_config_gateway,
            mock_config_gateway,
            mock_console_gateway,
            existing_config,
            tmp_path,
        ):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = existing_config
            options = InitOptions(reset_memory=True, reindex=False)

            with (
                patch("zk_chat.cli._run_upgraders"),
                patch("zk_chat.cli.validate_gateway_selection") as mock_validate,
                patch("zk_chat.cli._reset_smart_memory") as mock_reset,
            ):
                mock_validate.return_value = GatewayValidationResult(
                    gateway=ModelGateway.OLLAMA, changed=False, error=None
                )

                result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is None
            mock_reset.assert_called_once()

        def should_trigger_reindex_when_reindex_is_true(
            self,
            mock_global_config_gateway,
            mock_config_gateway,
            mock_console_gateway,
            existing_config,
            tmp_path,
        ):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = existing_config
            options = InitOptions(reindex=True, full=False)

            with (
                patch("zk_chat.cli._run_upgraders"),
                patch("zk_chat.cli.validate_gateway_selection") as mock_validate,
                patch("zk_chat.cli.reindex") as mock_reindex,
            ):
                mock_validate.return_value = GatewayValidationResult(
                    gateway=ModelGateway.OLLAMA, changed=False, error=None
                )

                common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            mock_reindex.assert_called_once_with(
                existing_config, mock_config_gateway, force_full=False, console_gateway=mock_console_gateway
            )

    class DescribeWithNewVault:
        def should_return_none_when_config_init_fails(
            self, mock_global_config_gateway, mock_config_gateway, mock_console_gateway, tmp_path
        ):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = None
            options = InitOptions()

            with patch("zk_chat.cli._initialize_config", return_value=None):
                result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is None

        def should_return_config_after_initial_reindex(
            self,
            mock_global_config_gateway,
            mock_config_gateway,
            mock_console_gateway,
            existing_config,
            tmp_path,
        ):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = None
            options = InitOptions()

            with (
                patch("zk_chat.cli._initialize_config", return_value=existing_config),
                patch("zk_chat.cli.reindex") as mock_reindex,
            ):
                result = common_init(options, mock_global_config_gateway, mock_config_gateway, mock_console_gateway)

            assert result is existing_config
            mock_reindex.assert_called_once_with(
                existing_config, mock_config_gateway, force_full=True, console_gateway=mock_console_gateway
            )


class DescribeSymlinkedVaultEquivalence:
    """Tests that symlinked vault paths are treated as the same vault as their target."""

    def should_store_resolved_path_when_saving_bookmark_via_symlink(self, tmp_path):
        real = tmp_path / "real"
        real.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real)

        mock_gcg = Mock(spec=GlobalConfigGateway)
        mock_console = Mock(spec=ConsoleGateway)
        global_config = GlobalConfig()

        _handle_save(InitOptions(vault=str(link), save=True), global_config, mock_gcg, mock_console)

        saved_config = mock_gcg.save.call_args[0][0]
        expected_path = normalize_vault_path(real)
        assert saved_config.bookmarks == {expected_path}
        assert saved_config.last_opened_bookmark == expected_path

    def should_find_existing_bookmark_when_resolving_via_symlink(self, tmp_path):
        real = tmp_path / "real"
        real.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real)

        mock_gcg = Mock(spec=GlobalConfigGateway)
        mock_console = Mock(spec=ConsoleGateway)
        canonical = normalize_vault_path(real)
        global_config = GlobalConfig(bookmarks={canonical}, last_opened_bookmark=canonical)

        result = _resolve_vault_path(InitOptions(vault=str(link)), global_config, mock_gcg, mock_console)

        assert result == canonical

    def should_keep_one_bookmark_for_same_vault_added_twice_via_different_paths(self, tmp_path):
        real = tmp_path / "real"
        real.mkdir()
        link = tmp_path / "link"
        link.symlink_to(real)

        global_config = GlobalConfig()
        mock_gcg = Mock(spec=GlobalConfigGateway)
        mock_console = Mock(spec=ConsoleGateway)

        _handle_save(InitOptions(vault=str(real), save=True), global_config, mock_gcg, mock_console)
        _handle_save(InitOptions(vault=str(link), save=True), global_config, mock_gcg, mock_console)

        assert len(global_config.bookmarks) == 1

    def should_treat_two_distinct_vaults_as_different_bookmarks(self, tmp_path):
        vault_a = tmp_path / "a"
        vault_b = tmp_path / "b"
        vault_a.mkdir()
        vault_b.mkdir()

        global_config = GlobalConfig()
        mock_gcg = Mock(spec=GlobalConfigGateway)
        mock_console = Mock(spec=ConsoleGateway)

        _handle_save(InitOptions(vault=str(vault_a), save=True), global_config, mock_gcg, mock_console)
        _handle_save(InitOptions(vault=str(vault_b), save=True), global_config, mock_gcg, mock_console)

        assert len(global_config.bookmarks) == 2
        assert normalize_vault_path(vault_a) in global_config.bookmarks
        assert normalize_vault_path(vault_b) in global_config.bookmarks
