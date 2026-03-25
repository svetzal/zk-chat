"""
Pure functions for configuration resolution logic.

These functions contain no side effects and are fully testable without mocking I/O.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from zk_chat.config import ModelGateway


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
    """
    Validate a requested gateway selection against current state.

    Parameters
    ----------
    requested : str | None
        The requested gateway name (e.g. "ollama", "openai"), or None/empty to keep current.
    current_gateway : ModelGateway
        The currently configured gateway.
    openai_key_present : bool
        Whether the OPENAI_API_KEY environment variable is set.

    Returns
    -------
    GatewayValidationResult
        Result containing the resolved gateway, whether it changed, and any error.
    """
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

    if new_gateway == ModelGateway.OPENAI and not openai_key_present:
        return GatewayValidationResult(
            gateway=current_gateway,
            changed=False,
            error="OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.",
        )

    changed = new_gateway != current_gateway
    return GatewayValidationResult(gateway=new_gateway, changed=changed)


def resolve_vault_from_args(
    arg_vault: str | None,
    bookmarks: list[str],
    last_opened: str | None,
) -> VaultResolutionResult:
    """
    Resolve the vault path from CLI arguments or bookmark history.

    This function contains only the pure decision logic — no filesystem checks.

    Parameters
    ----------
    arg_vault : str | None
        Vault path provided via CLI argument (already resolved to absolute path by caller).
    bookmarks : list[str]
        List of known bookmarked vault paths.
    last_opened : str | None
        The last-opened bookmarked vault path, if any.

    Returns
    -------
    VaultResolutionResult
        Result with the resolved path and how it was determined.
    """
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
    """
    Determine what action to take for model selection.

    Parameters
    ----------
    model_arg : str | None
        The model name from CLI args. None or "choose" triggers interactive selection.
    available_models : list[str]
        Models available from the current gateway.

    Returns
    -------
    ModelActionResult
        Result describing whether to use a specific model or prompt interactively.
    """
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
    """
    Resolve the visual model selection from a combo-box string.

    Parameters
    ----------
    selected_text : str
        The text currently selected in the visual model combo box.
    none_sentinel : str
        The sentinel string that represents "no visual model".

    Returns
    -------
    str | None
        None if the sentinel was selected, otherwise the selected model name.
    """
    if selected_text == none_sentinel:
        return None
    return selected_text


def determine_init_config_action(
    gateway_arg: str | None,
    model_arg: str | None,
    visual_model_arg: str | None,
    openai_key_present: bool,
) -> InitConfigAction:
    """
    Determine all decisions needed to initialize a new vault configuration.

    Encodes the branching logic for gateway selection, chat model selection,
    and visual model selection without performing any I/O.

    Parameters
    ----------
    gateway_arg : str | None
        The requested gateway name ("ollama", "openai"), or None to default to OLLAMA.
    model_arg : str | None
        The model name from CLI args. None or "choose" triggers interactive selection.
    visual_model_arg : str | None
        The visual model arg from CLI. "choose" triggers selection, specific name uses it,
        None applies default rules.
    openai_key_present : bool
        Whether the OPENAI_API_KEY environment variable is set.

    Returns
    -------
    InitConfigAction
        Fully describes what the shell function should do for gateway, chat model, and visual model.
    """
    # Resolve gateway
    gateway = ModelGateway(gateway_arg) if gateway_arg else ModelGateway.OLLAMA
    if gateway == ModelGateway.OPENAI and not openai_key_present:
        return InitConfigAction(
            gateway=ModelGateway.OLLAMA,
            error="Error: OPENAI_API_KEY environment variable is not set. Cannot use OpenAI gateway.",
        )

    # Chat model decisions
    needs_chat_model_selection = model_arg is None or model_arg == "choose"
    chat_model_name = None if needs_chat_model_selection else model_arg

    # Visual model decisions
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
    """
    Determine what model updates to perform when a vault config already exists.

    Parameters
    ----------
    model_arg : str | None
        The model arg from CLI. None means no update; "choose" means interactive selection.
    visual_model_arg : str | None
        The visual model arg from CLI. None means no update; "choose" means interactive selection.
    has_existing_visual_model : bool
        Whether the config already has a visual model configured.

    Returns
    -------
    ModelUpdateAction
        Describes whether to update chat model, visual model, and whether to prompt.
    """
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
