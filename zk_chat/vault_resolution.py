"""Pure vault path resolution logic, decoupled from CLI output."""

import os
from pathlib import Path

from zk_chat.global_config_gateway import GlobalConfigGateway


class VaultResolutionError(Exception):
    pass


def resolve_vault_path(vault: Path | None, global_config_gateway: GlobalConfigGateway) -> str:
    """Resolve the vault path from an explicit argument or the global config bookmarks.

    Parameters
    ----------
    vault : Path | None
        Explicitly provided vault path, or None to fall back to bookmarks.
    global_config_gateway : GlobalConfigGateway
        Gateway used to load the global configuration when no vault is given.

    Returns
    -------
    str
        The resolved, absolute vault path.

    Raises
    ------
    VaultResolutionError
        If no vault path can be determined or the resolved path does not exist.
    """
    if vault:
        vault_path = str(vault.resolve())
    else:
        global_config = global_config_gateway.load()
        vault_path = global_config.get_last_opened_bookmark_path()
        if not vault_path:
            raise VaultResolutionError("No vault specified and no bookmarks found.")
    if not os.path.exists(vault_path):
        raise VaultResolutionError(f"Vault path '{vault_path}' does not exist.")
    return vault_path
