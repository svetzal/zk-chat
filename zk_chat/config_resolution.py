"""
Pure functions for configuration resolution logic.

These functions contain no side effects and are fully testable without mocking I/O.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from zk_chat.config import ModelGateway

OPENAI_KEY_MISSING_ERROR = "OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway."


def check_openai_key_required(gateway: ModelGateway, openai_key_present: bool) -> str | None:
    """Return an error message if gateway is OpenAI and the key is missing, else None."""
    if gateway == ModelGateway.OPENAI and not openai_key_present:
        return OPENAI_KEY_MISSING_ERROR
    return None


class InitConfigAction(BaseModel):
    """
    Describes all decisions needed to initialize a new vault configuration.

    Produced by determine_init_config_action; consumed by _initialize_config shell.
    """

    model_config = ConfigDict(frozen=True)

    gateway: ModelGateway
    error: str | None = None

    needs_chat_model_selection: bool = False
    chat_model_name: str | None = None

    needs_visual_model_selection: bool = False
    use_chat_model_for_visual: bool = False
    needs_visual_model_prompt: bool = False
    visual_model_name: str | None = None


class ModelUpdateAction(BaseModel):
    """
    Describes what model updates to perform when a vault config already exists.

    Produced by determine_model_update_action; consumed by _maybe_update_models shell.
    """

    model_config = ConfigDict(frozen=True)

    update_chat_model: bool
    chat_model_name: str | None
    prompt_for_visual_model: bool
    update_visual_model: bool
    visual_model_name: str | None


class GatewayValidationResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    gateway: ModelGateway
    changed: bool
    error: str | None = None


class VaultResolutionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    vault_path: str | None
    source: Literal["argument", "last_opened", "none"]
    error: str | None = None


class ModelActionResult(BaseModel):
    model_config = ConfigDict(frozen=True)

    model_name: str | None
    needs_interactive_selection: bool
    error: str | None = None


def validate_gateway_selection(
    requested: str | None,
    current_gateway: ModelGateway,
    openai_key_present: bool,
) -> GatewayValidationResult:
    if not requested:
        return GatewayValidationResult(gateway=current_gateway, changed=False)

    try:
        new_gateway = ModelGateway(requested)
    except ValueError:
        return GatewayValidationResult(
            gateway=current_gateway,
            changed=False,
            error=f"Invalid gateway '{requested}'. Valid options are: {', '.join(g.value for g in ModelGateway)}",
        )

    error = check_openai_key_required(new_gateway, openai_key_present)
    if error:
        return GatewayValidationResult(gateway=current_gateway, changed=False, error=error)

    changed = new_gateway != current_gateway
    return GatewayValidationResult(gateway=new_gateway, changed=changed)


def resolve_vault_from_args(
    arg_vault: str | None,
    bookmarks: list[str],
    last_opened: str | None,
) -> VaultResolutionResult:
    if arg_vault:
        return VaultResolutionResult(vault_path=arg_vault, source="argument")

    if last_opened and last_opened in bookmarks:
        return VaultResolutionResult(vault_path=last_opened, source="last_opened")

    return VaultResolutionResult(
        vault_path=None,
        source="none",
        error="No vault specified. Use --vault or set a bookmark first.",
    )


def determine_model_action(
    model_arg: str | None,
    available_models: list[str],
) -> ModelActionResult:
    if model_arg is None or model_arg == "choose":
        return ModelActionResult(model_name=None, needs_interactive_selection=True)

    if model_arg in available_models:
        return ModelActionResult(model_name=model_arg, needs_interactive_selection=False)

    return ModelActionResult(
        model_name=None,
        needs_interactive_selection=True,
        error=f"Model '{model_arg}' not found in available models.",
    )


def resolve_visual_model_selection(
    selected_text: str,
    none_sentinel: str = "None - Disable Visual Analysis",
) -> str | None:
    if selected_text == none_sentinel:
        return None
    return selected_text


def determine_init_config_action(
    gateway_arg: str | None,
    model_arg: str | None,
    visual_model_arg: str | None,
    openai_key_present: bool,
) -> InitConfigAction:
    """Pure function — encodes all branching logic for gateway/chat/visual model without I/O."""
    gateway = ModelGateway(gateway_arg) if gateway_arg else ModelGateway.OLLAMA
    error = check_openai_key_required(gateway, openai_key_present)
    if error:
        return InitConfigAction(gateway=ModelGateway.OLLAMA, error=error)

    needs_chat_model_selection = model_arg is None or model_arg == "choose"
    chat_model_name = None if needs_chat_model_selection else model_arg

    if visual_model_arg == "choose":
        return InitConfigAction(
            gateway=gateway,
            needs_chat_model_selection=needs_chat_model_selection,
            chat_model_name=chat_model_name,
            needs_visual_model_selection=True,
        )
    if visual_model_arg is not None:
        return InitConfigAction(
            gateway=gateway,
            needs_chat_model_selection=needs_chat_model_selection,
            chat_model_name=chat_model_name,
            visual_model_name=visual_model_arg,
        )
    if not needs_chat_model_selection:
        # Model was explicitly specified — use it as visual model too
        return InitConfigAction(
            gateway=gateway,
            needs_chat_model_selection=False,
            chat_model_name=chat_model_name,
            use_chat_model_for_visual=True,
        )
    # Model was interactive — ask user whether they want a visual model
    return InitConfigAction(
        gateway=gateway,
        needs_chat_model_selection=True,
        needs_visual_model_prompt=True,
    )


def determine_model_update_action(
    model_arg: str | None,
    visual_model_arg: str | None,
    has_existing_visual_model: bool,
) -> ModelUpdateAction:
    update_chat_model = model_arg is not None
    chat_model_name = None if model_arg in (None, "choose") else model_arg

    # Only prompt for visual model when choosing chat model interactively and no visual is set
    prompt_for_visual_model = model_arg == "choose" and not visual_model_arg and not has_existing_visual_model

    update_visual_model = bool(visual_model_arg)
    visual_model_name = None if visual_model_arg == "choose" else visual_model_arg

    return ModelUpdateAction(
        update_chat_model=update_chat_model,
        chat_model_name=chat_model_name,
        prompt_for_visual_model=prompt_for_visual_model,
        update_visual_model=update_visual_model,
        visual_model_name=visual_model_name,
    )
