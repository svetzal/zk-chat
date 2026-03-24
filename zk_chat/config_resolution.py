"""
Pure functions for configuration resolution logic.

These functions contain no side effects and are fully testable without mocking I/O.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from zk_chat.config import ModelGateway


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
