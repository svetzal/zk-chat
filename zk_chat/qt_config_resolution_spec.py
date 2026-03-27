"""
Tests for qt_config_resolution pure functions.
"""

from zk_chat.config import Config, ModelGateway
from zk_chat.qt_config_resolution import (
    resolve_config_for_vault,
    resolve_gui_vault_init,
    resolve_settings_change,
)


class DescribeResolveSettingsChange:
    """Tests for the resolve_settings_change pure function."""

    def should_return_vault_changed_false_when_vault_path_unchanged(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.vault_changed is False

    def should_return_vault_changed_true_when_vault_path_differs(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/new-vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.vault_changed is True

    def should_use_loaded_config_when_vault_changes_and_config_exists(self):
        current_config = Config(vault="/vault", model="old-model", gateway=ModelGateway.OLLAMA)
        loaded_config = Config(vault="/new-vault", model="loaded-model", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=current_config,
            new_vault_path="/new-vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="chosen-model",
            visual_model_text="None - Disable Visual Analysis",
            loaded_config_for_new_vault=loaded_config,
        )

        assert result.updated_config.vault == "/new-vault"
        assert result.updated_config.model == "chosen-model"

    def should_create_new_config_when_vault_changes_and_no_existing_config(self):
        current_config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=current_config,
            new_vault_path="/new-vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
            loaded_config_for_new_vault=None,
        )

        assert result.updated_config.vault == "/new-vault"

    def should_update_gateway_on_existing_config(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/vault",
            new_gateway=ModelGateway.OPENAI,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.updated_config.gateway == ModelGateway.OPENAI

    def should_update_chat_model_on_existing_config(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="mistral",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.updated_config.model == "mistral"

    def should_resolve_visual_model_to_none_when_sentinel_selected(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.updated_config.visual_model is None

    def should_resolve_visual_model_to_name_when_model_selected(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="llava",
        )

        assert result.updated_config.visual_model == "llava"

    def should_set_new_bookmark_path_when_vault_changed(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/new-vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.new_bookmark_path == "/new-vault"

    def should_not_set_new_bookmark_path_when_vault_unchanged(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.new_bookmark_path is None

    def should_set_updated_global_config_needed_when_vault_changes(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/new-vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.updated_global_config_needed is True

    def should_not_need_global_config_update_when_vault_unchanged(self):
        config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)

        result = resolve_settings_change(
            current_config=config,
            new_vault_path="/vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
        )

        assert result.updated_global_config_needed is False

    def should_preserve_chunk_settings_from_loaded_config_when_vault_changes(self):
        current_config = Config(vault="/vault", model="llama3", gateway=ModelGateway.OLLAMA)
        loaded_config = Config(vault="/new-vault", model="llama3", gateway=ModelGateway.OLLAMA, chunk_size=1000)

        result = resolve_settings_change(
            current_config=current_config,
            new_vault_path="/new-vault",
            new_gateway=ModelGateway.OLLAMA,
            new_chat_model="llama3",
            visual_model_text="None - Disable Visual Analysis",
            loaded_config_for_new_vault=loaded_config,
        )

        assert result.updated_config.chunk_size == 1000


class DescribeResolveGuiVaultInit:
    """Tests for the resolve_gui_vault_init pure function."""

    def should_return_last_opened_when_bookmark_path_exists(self):
        result = resolve_gui_vault_init(
            last_opened_bookmark_path="/my-vault",
            user_selected_path=None,
        )

        assert result.vault_path == "/my-vault"
        assert result.source == "last_opened"

    def should_return_user_selected_when_no_bookmark_but_user_selected(self):
        result = resolve_gui_vault_init(
            last_opened_bookmark_path=None,
            user_selected_path="/selected-vault",
        )

        assert result.vault_path == "/selected-vault"
        assert result.source == "user_selected"

    def should_return_none_when_both_are_none(self):
        result = resolve_gui_vault_init(
            last_opened_bookmark_path=None,
            user_selected_path=None,
        )

        assert result.vault_path is None
        assert result.source == "none"

    def should_set_needs_bookmark_update_for_user_selected_path(self):
        result = resolve_gui_vault_init(
            last_opened_bookmark_path=None,
            user_selected_path="/selected-vault",
        )

        assert result.needs_bookmark_update is True

    def should_not_need_bookmark_update_for_last_opened(self):
        result = resolve_gui_vault_init(
            last_opened_bookmark_path="/my-vault",
            user_selected_path=None,
        )

        assert result.needs_bookmark_update is False

    def should_prefer_last_opened_over_user_selected(self):
        result = resolve_gui_vault_init(
            last_opened_bookmark_path="/my-vault",
            user_selected_path="/selected-vault",
        )

        assert result.vault_path == "/my-vault"
        assert result.source == "last_opened"


class DescribeResolveConfigForVault:
    """Tests for the resolve_config_for_vault pure function."""

    def should_return_loaded_config_when_not_none(self):
        loaded = Config(vault="/vault", model="llama3")

        config, was_created = resolve_config_for_vault(loaded, "/vault")

        assert config is loaded

    def should_create_default_config_when_loaded_is_none(self):
        config, _ = resolve_config_for_vault(None, "/vault")

        assert config.vault == "/vault"
        assert config.model == ""

    def should_set_was_created_true_when_creating_default(self):
        _, was_created = resolve_config_for_vault(None, "/vault")

        assert was_created is True

    def should_set_was_created_false_when_using_loaded(self):
        loaded = Config(vault="/vault", model="llama3")

        _, was_created = resolve_config_for_vault(loaded, "/vault")

        assert was_created is False
