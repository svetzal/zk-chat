import os
from typing import Dict, Optional, Set
from pydantic import BaseModel


def get_global_config_path() -> str:
    """Get the path to the global config file in the user's home directory."""
    return os.path.expanduser("~/.zk_chat")


class GlobalConfig(BaseModel):
    """
    Global configuration for zk_chat that persists across sessions.
    Stores bookmarks and the last opened bookmark.
    """
    bookmarks: Set[str] = set()  # set of absolute vault paths
    last_opened_bookmark: Optional[str] = None  # absolute path of the last opened bookmark

    @classmethod
    def load(cls) -> 'GlobalConfig':
        """Load the global config from ~/.zk_chat or create a new one if it doesn't exist."""
        config_path = get_global_config_path()
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return cls.model_validate_json(f.read())
            except Exception:
                # If there's an error loading the config, create a new one
                return cls()
        else:
            return cls()

    def save(self) -> None:
        """Save the global config to ~/.zk_chat."""
        config_path = get_global_config_path()
        with open(config_path, 'w') as f:
            f.write(self.model_dump_json(indent=2))

    def add_bookmark(self, vault_path: str) -> None:
        """Add a bookmark with the given vault path."""
        abs_path = os.path.abspath(vault_path)
        self.bookmarks.add(abs_path)
        self.save()

    def remove_bookmark(self, vault_path: str) -> bool:
        """Remove a bookmark with the given vault path. Returns True if successful."""
        abs_path = os.path.abspath(vault_path)
        if abs_path in self.bookmarks:
            self.bookmarks.remove(abs_path)
            # If we're removing the last opened bookmark, clear it
            if self.last_opened_bookmark == abs_path:
                self.last_opened_bookmark = None
            self.save()
            return True
        return False

    def get_bookmark(self, vault_path: str) -> Optional[str]:
        """Get the absolute path for a bookmark with the given path."""
        abs_path = os.path.abspath(vault_path)
        return abs_path if abs_path in self.bookmarks else None

    def set_last_opened_bookmark(self, vault_path: str) -> bool:
        """Set the last opened bookmark. Returns True if successful."""
        abs_path = os.path.abspath(vault_path)
        if abs_path in self.bookmarks:
            self.last_opened_bookmark = abs_path
            self.save()
            return True
        return False

    def get_last_opened_bookmark_path(self) -> Optional[str]:
        """Get the path for the last opened bookmark."""
        if self.last_opened_bookmark and self.last_opened_bookmark in self.bookmarks:
            return self.last_opened_bookmark
        return None

