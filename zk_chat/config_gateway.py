"""
Gateway for vault configuration persistence.

Thin I/O wrapper that handles reading and writing the .zk_chat configuration
file within a vault directory. Follows the gateway pattern used throughout
zk-chat to isolate file I/O from the pure Config data model.
"""

import os

from zk_chat.config import Config


class ConfigGateway:
    """
    Thin I/O wrapper for vault config persistence.

    Handles reading and writing the .zk_chat file in a vault directory.
    No business logic lives here — all validation and defaults belong in Config.
    """

    def load(self, vault_path: str) -> Config | None:
        """
        Load config from the .zk_chat file in the given vault, or return None.

        Parameters
        ----------
        vault_path : str
            Absolute path to the vault directory.

        Returns
        -------
        Config | None
            Loaded configuration, or None if no config file exists.
        """
        config_path = os.path.join(vault_path, ".zk_chat")
        if os.path.exists(config_path):
            with open(config_path) as f:
                return Config.model_validate_json(f.read())
        return None

    def save(self, config: Config) -> None:
        """
        Write config to the .zk_chat file in the vault.

        Parameters
        ----------
        config : Config
            Configuration to persist. The vault path is taken from config.vault.
        """
        config_path = os.path.join(config.vault, ".zk_chat")
        with open(config_path, "w") as f:
            f.write(config.model_dump_json(indent=2))
