from unittest.mock import Mock, patch

import pytest

from zk_chat.cli import common_init
from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.config_resolution import GatewayValidationResult
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.init_options import InitOptions


@pytest.fixture
def mock_global_config_gateway():
    gateway = Mock(spec=GlobalConfigGateway)
    gateway.load.return_value = GlobalConfig()
    return gateway


@pytest.fixture
def mock_config_gateway():
    return Mock(spec=ConfigGateway)


@pytest.fixture
def existing_config(tmp_path):
    return Config(vault=str(tmp_path), model="llama3", gateway=ModelGateway.OLLAMA)


class DescribeCommonInit:
    """Tests for the common_init orchestration function."""

    class DescribeWithSaveOption:
        def should_return_none_when_save_set_without_vault(self, mock_global_config_gateway, mock_config_gateway):
            options = InitOptions(save=True, vault=None)

            result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is None

        def should_return_none_when_save_set_with_nonexistent_vault(
            self, mock_global_config_gateway, mock_config_gateway
        ):
            options = InitOptions(save=True, vault="/no/such/path")

            result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is None

        def should_return_none_and_save_bookmark_when_vault_exists(
            self, mock_global_config_gateway, mock_config_gateway, tmp_path
        ):
            global_config = GlobalConfig()
            mock_global_config_gateway.load.return_value = global_config
            options = InitOptions(save=True, vault=str(tmp_path))

            result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is None
            mock_global_config_gateway.save.assert_called_once_with(global_config)

    class DescribeWithNoVaultAvailable:
        def should_return_none_when_no_vault_and_no_bookmarks(self, mock_global_config_gateway, mock_config_gateway):
            options = InitOptions()

            result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is None

    class DescribeWithExistingConfig:
        def should_return_config_when_vault_exists_with_config(
            self, mock_global_config_gateway, mock_config_gateway, existing_config, tmp_path
        ):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = existing_config
            options = InitOptions(reindex=False)

            with patch("zk_chat.cli._run_upgraders"), patch("zk_chat.cli.validate_gateway_selection") as mock_validate:
                mock_validate.return_value = Mock(
                    spec=GatewayValidationResult, gateway=ModelGateway.OLLAMA, changed=False, error=None
                )

                result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is existing_config

        def should_return_none_when_reset_memory_is_true(
            self, mock_global_config_gateway, mock_config_gateway, existing_config, tmp_path
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
                mock_validate.return_value = Mock(
                    spec=GatewayValidationResult, gateway=ModelGateway.OLLAMA, changed=False, error=None
                )

                result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is None
            mock_reset.assert_called_once()

        def should_trigger_reindex_when_reindex_is_true(
            self, mock_global_config_gateway, mock_config_gateway, existing_config, tmp_path
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
                mock_validate.return_value = Mock(
                    spec=GatewayValidationResult, gateway=ModelGateway.OLLAMA, changed=False, error=None
                )

                common_init(options, mock_global_config_gateway, mock_config_gateway)

            mock_reindex.assert_called_once_with(existing_config, mock_config_gateway, force_full=False)

    class DescribeWithNewVault:
        def should_return_none_when_config_init_fails(self, mock_global_config_gateway, mock_config_gateway, tmp_path):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = None
            options = InitOptions()

            with patch("zk_chat.cli._initialize_config", return_value=None):
                result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is None

        def should_return_config_after_initial_reindex(
            self, mock_global_config_gateway, mock_config_gateway, existing_config, tmp_path
        ):
            global_config = GlobalConfig(bookmarks={str(tmp_path)}, last_opened_bookmark=str(tmp_path))
            mock_global_config_gateway.load.return_value = global_config
            mock_config_gateway.load.return_value = None
            options = InitOptions()

            with (
                patch("zk_chat.cli._initialize_config", return_value=existing_config),
                patch("zk_chat.cli.reindex") as mock_reindex,
            ):
                result = common_init(options, mock_global_config_gateway, mock_config_gateway)

            assert result is existing_config
            mock_reindex.assert_called_once_with(existing_config, mock_config_gateway, force_full=True)

    class DescribeGatewayDefaults:
        def should_construct_default_gateways_when_none_provided(self, tmp_path):
            options = InitOptions(save=True, vault=str(tmp_path))

            with (
                patch("zk_chat.cli.GlobalConfigGateway") as mock_gcg_cls,
                patch("zk_chat.cli.ConfigGateway"),
            ):
                mock_gcg = Mock(spec=GlobalConfigGateway)
                mock_gcg.load.return_value = GlobalConfig()
                mock_gcg_cls.return_value = mock_gcg

                common_init(options)

            mock_gcg_cls.assert_called_once()
