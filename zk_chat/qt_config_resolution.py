"""
Pure functions for Qt GUI configuration resolution logic.

These functions contain no side effects and are fully testable without mocking I/O.
"""

from typing import Literal

from pydantic import BaseModel, ConfigDict

from zk_chat.config import Config, ModelGateway
from zk_chat.config_resolution import resolve_visual_model_selection


class SettingsChangeResult(BaseModel):
    """
    Describes all changes to persist when the user saves the settings dialog.

    Produced by resolve_settings_change; consumed by SettingsDialog.save_settings shell.
    """

    model_config = ConfigDict(frozen=True)

    updated_config: Config
    vault_changed: bool
    updated_global_config_needed: bool
    new_bookmark_path: str | None = None


class VaultInitResult(BaseModel):
    """
    Describes the outcome of resolving the initial vault for the GUI.

    Produced by resolve_gui_vault_init; consumed by MainWindow.__init__ shell.
    """

    model_config = ConfigDict(frozen=True)

    vault_path: str | None
    source: Literal["last_opened", "user_selected", "none"]
    needs_bookmark_update: bool
    needs_config_creation: bool


def resolve_settings_change(
    current_config: Config,
    new_vault_path: str,
    new_gateway: ModelGateway,
    new_chat_model: str,
    visual_model_text: str,
    loaded_config_for_new_vault: Config | None = None,
    none_sentinel: str = "None - Disable Visual Analysis",
) -> SettingsChangeResult:
    """
    Determine all changes to persist when the user saves the settings dialog.

    Parameters
    ----------
    current_config : Config
        The configuration currently loaded in the dialog.
    new_vault_path : str
        The vault path entered or selected in the dialog.
    new_gateway : ModelGateway
        The gateway selected in the dialog.
    new_chat_model : str
        The chat model selected in the dialog.
    visual_model_text : str
        The visual model combo-box text selected in the dialog.
    loaded_config_for_new_vault : Config | None
        Config loaded from disk for the new vault (when vault changed), or None if
        no config file exists or the vault path is unchanged.
    none_sentinel : str
        The sentinel string that represents "no visual model" in the combo box.

    Returns
    -------
    SettingsChangeResult
        All changes to apply, with no side effects performed.
    """
    vault_changed = new_vault_path != current_config.vault
    visual_model = resolve_visual_model_selection(visual_model_text, none_sentinel)

    if vault_changed:
        if loaded_config_for_new_vault is not None:
            updated_config = loaded_config_for_new_vault.model_copy(
                update={
                    "gateway": new_gateway,
                    "model": new_chat_model,
                    "visual_model": visual_model,
                }
            )
        else:
            updated_config = Config(
                vault=new_vault_path,
                model=new_chat_model,
                gateway=new_gateway,
                visual_model=visual_model,
            )
        return SettingsChangeResult(
            updated_config=updated_config,
            vault_changed=True,
            updated_global_config_needed=True,
            new_bookmark_path=new_vault_path,
        )

    updated_config = current_config.model_copy(
        update={
            "gateway": new_gateway,
            "model": new_chat_model,
            "visual_model": visual_model,
        }
    )
    return SettingsChangeResult(
        updated_config=updated_config,
        vault_changed=False,
        updated_global_config_needed=False,
    )


def resolve_gui_vault_init(
    last_opened_bookmark_path: str | None,
    user_selected_path: str | None,
) -> VaultInitResult:
    """
    Determine the initial vault path for the GUI application.

    Parameters
    ----------
    last_opened_bookmark_path : str | None
        Path to the last-opened bookmark from global config, or None if none exists.
    user_selected_path : str | None
        Path selected by the user via a file dialog, or None if not selected.

    Returns
    -------
    VaultInitResult
        Result with the resolved vault path and what actions the shell must take.
    """
    if last_opened_bookmark_path is not None:
        return VaultInitResult(
            vault_path=last_opened_bookmark_path,
            source="last_opened",
            needs_bookmark_update=False,
            needs_config_creation=False,
        )
    if user_selected_path is not None:
        return VaultInitResult(
            vault_path=user_selected_path,
            source="user_selected",
            needs_bookmark_update=True,
            needs_config_creation=False,
        )
    return VaultInitResult(
        vault_path=None,
        source="none",
        needs_bookmark_update=False,
        needs_config_creation=False,
    )


def resolve_config_for_vault(
    loaded_config: Config | None,
    vault_path: str,
) -> tuple[Config, bool]:
    """
    Determine the active config for a vault, creating a default if none exists.

    Parameters
    ----------
    loaded_config : Config | None
        Config loaded from disk for the vault, or None if no config file exists.
    vault_path : str
        The vault path for which to resolve config.

    Returns
    -------
    tuple[Config, bool]
        A (config, was_created) pair. If loaded_config is None, a minimal default
        Config is created and was_created is True. Otherwise was_created is False.
    """
    if loaded_config is None:
        return (Config(vault=vault_path, model=""), True)
    return (loaded_config, False)
