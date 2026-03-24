"""
Tests for config_resolution pure functions.
"""

from zk_chat.config import ModelGateway
from zk_chat.config_resolution import (
    GatewayValidationResult,
    ModelActionResult,
    VaultResolutionResult,
    determine_model_action,
    resolve_vault_from_args,
    resolve_visual_model_selection,
    validate_gateway_selection,
)


class DescribeValidateGatewaySelection:
    """Tests for the validate_gateway_selection pure function."""

    def should_return_current_gateway_unchanged_when_requested_is_none(self):
        result = validate_gateway_selection(None, ModelGateway.OLLAMA, openai_key_present=False)

        assert result.gateway == ModelGateway.OLLAMA
        assert result.changed is False
        assert result.error is None

    def should_return_current_gateway_unchanged_when_requested_is_empty_string(self):
        result = validate_gateway_selection("", ModelGateway.OLLAMA, openai_key_present=False)

        assert result.gateway == ModelGateway.OLLAMA
        assert result.changed is False
        assert result.error is None

    def should_return_error_when_openai_requested_without_api_key(self):
        result = validate_gateway_selection("openai", ModelGateway.OLLAMA, openai_key_present=False)

        assert result.gateway == ModelGateway.OLLAMA
        assert result.changed is False
        assert result.error is not None
        assert "OPENAI_API_KEY" in result.error

    def should_return_openai_gateway_when_key_is_present(self):
        result = validate_gateway_selection("openai", ModelGateway.OLLAMA, openai_key_present=True)

        assert result.gateway == ModelGateway.OPENAI
        assert result.changed is True
        assert result.error is None

    def should_indicate_no_change_when_requested_matches_current(self):
        result = validate_gateway_selection("ollama", ModelGateway.OLLAMA, openai_key_present=False)

        assert result.gateway == ModelGateway.OLLAMA
        assert result.changed is False
        assert result.error is None

    def should_return_error_for_invalid_gateway_name(self):
        result = validate_gateway_selection("invalid_gateway", ModelGateway.OLLAMA, openai_key_present=False)

        assert result.gateway == ModelGateway.OLLAMA
        assert result.changed is False
        assert result.error is not None
        assert "invalid_gateway" in result.error

    def should_return_changed_true_when_switching_from_openai_to_ollama(self):
        result = validate_gateway_selection("ollama", ModelGateway.OPENAI, openai_key_present=True)

        assert result.gateway == ModelGateway.OLLAMA
        assert result.changed is True
        assert result.error is None

    def should_return_correct_type(self):
        result = validate_gateway_selection("ollama", ModelGateway.OLLAMA, openai_key_present=False)

        assert isinstance(result, GatewayValidationResult)


class DescribeResolveVaultFromArgs:
    """Tests for the resolve_vault_from_args pure function."""

    def should_return_argument_path_when_arg_vault_provided(self):
        result = resolve_vault_from_args("/abs/vault", ["/abs/vault"], "/abs/vault")

        assert result.vault_path == "/abs/vault"
        assert result.source == "argument"
        assert result.error is None

    def should_return_argument_path_even_when_not_in_bookmarks(self):
        result = resolve_vault_from_args("/new/vault", [], None)

        assert result.vault_path == "/new/vault"
        assert result.source == "argument"
        assert result.error is None

    def should_return_last_opened_when_no_arg_and_bookmark_exists(self):
        result = resolve_vault_from_args(None, ["/bookmarked/vault"], "/bookmarked/vault")

        assert result.vault_path == "/bookmarked/vault"
        assert result.source == "last_opened"
        assert result.error is None

    def should_return_none_and_error_when_no_arg_and_no_bookmarks(self):
        result = resolve_vault_from_args(None, [], None)

        assert result.vault_path is None
        assert result.source == "none"
        assert result.error is not None
        assert "vault" in result.error.lower()

    def should_return_none_when_last_opened_not_in_bookmarks(self):
        result = resolve_vault_from_args(None, ["/other/vault"], "/missing/vault")

        assert result.vault_path is None
        assert result.source == "none"
        assert result.error is not None

    def should_return_none_when_last_opened_is_none_and_bookmarks_exist(self):
        result = resolve_vault_from_args(None, ["/some/vault"], None)

        assert result.vault_path is None
        assert result.source == "none"
        assert result.error is not None

    def should_prefer_arg_vault_over_last_opened(self):
        result = resolve_vault_from_args("/explicit/vault", ["/bookmarked/vault"], "/bookmarked/vault")

        assert result.vault_path == "/explicit/vault"
        assert result.source == "argument"

    def should_return_correct_type(self):
        result = resolve_vault_from_args(None, [], None)

        assert isinstance(result, VaultResolutionResult)


class DescribeDetermineModelAction:
    """Tests for the determine_model_action pure function."""

    def should_require_interactive_selection_when_model_arg_is_none(self):
        result = determine_model_action(None, ["model-a", "model-b"])

        assert result.needs_interactive_selection is True
        assert result.model_name is None
        assert result.error is None

    def should_require_interactive_selection_when_model_arg_is_choose(self):
        result = determine_model_action("choose", ["model-a", "model-b"])

        assert result.needs_interactive_selection is True
        assert result.model_name is None
        assert result.error is None

    def should_return_model_name_when_found_in_available(self):
        result = determine_model_action("model-a", ["model-a", "model-b"])

        assert result.model_name == "model-a"
        assert result.needs_interactive_selection is False
        assert result.error is None

    def should_require_interactive_when_model_not_in_available(self):
        result = determine_model_action("missing-model", ["model-a", "model-b"])

        assert result.needs_interactive_selection is True
        assert result.model_name is None
        assert result.error is not None
        assert "missing-model" in result.error

    def should_handle_empty_available_models_list(self):
        result = determine_model_action("some-model", [])

        assert result.needs_interactive_selection is True
        assert result.model_name is None
        assert result.error is not None

    def should_return_correct_type(self):
        result = determine_model_action(None, [])

        assert isinstance(result, ModelActionResult)


class DescribeResolveVisualModelSelection:
    """Tests for the resolve_visual_model_selection pure function."""

    def should_return_none_when_sentinel_selected(self):
        result = resolve_visual_model_selection("None - Disable Visual Analysis")

        assert result is None

    def should_return_model_name_when_not_sentinel(self):
        result = resolve_visual_model_selection("llama3.2-vision")

        assert result == "llama3.2-vision"

    def should_use_custom_sentinel(self):
        result = resolve_visual_model_selection("DISABLED", none_sentinel="DISABLED")

        assert result is None

    def should_return_model_name_with_custom_sentinel_when_different(self):
        result = resolve_visual_model_selection("some-model", none_sentinel="DISABLED")

        assert result == "some-model"

    def should_return_empty_string_when_empty_string_and_not_sentinel(self):
        result = resolve_visual_model_selection("")

        assert result == ""
