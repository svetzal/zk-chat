"""
Gateway for global configuration persistence.

Thin I/O wrapper that handles reading and writing the ~/.zk_chat global
configuration file. Follows the gateway pattern used throughout zk-chat
to isolate file I/O from the pure GlobalConfig data model.
"""

import os

from zk_chat.global_config import GlobalConfig


class GlobalConfigGateway:
    """
    Thin I/O wrapper for global config persistence (~/.zk_chat).

    Handles reading and writing the global config file. The config_path
    is injectable for testing without patching os.path.expanduser.
    """

    def __init__(self, config_path: str | None = None):
        """
        Initialize the gateway.

        Parameters
        ----------
        config_path : str | None
            Path to the global config file. Defaults to ~/.zk_chat.
            Pass an explicit path in tests to avoid touching the real config.
        """
        self._config_path = config_path or os.path.expanduser("~/.zk_chat")

    def load(self) -> GlobalConfig:
        """
        Load global config from disk, or return a fresh default if absent or corrupt.

        Returns
        -------
        GlobalConfig
            Loaded configuration, or a new default instance.
        """
        if os.path.exists(self._config_path):
            try:
                with open(self._config_path) as f:
                    return GlobalConfig.model_validate_json(f.read())
            except Exception:
                return GlobalConfig()
        return GlobalConfig()

    def save(self, config: GlobalConfig) -> None:
        """
        Write global config to disk.

        Parameters
        ----------
        config : GlobalConfig
            Configuration to persist.
        """
        with open(self._config_path, "w") as f:
            f.write(config.model_dump_json(indent=2))
