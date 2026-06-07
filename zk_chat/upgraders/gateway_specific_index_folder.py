import shutil
import sys
from pathlib import Path

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

from zk_chat.config import Config, ModelGateway


class Upgrader:
    """Base class for one-time migration steps applied to a vault on startup."""

    def should_run(self) -> bool:
        """Return ``True`` when this upgrader's preconditions are met and migration is needed."""
        return False

    def run(self) -> None:
        """Execute the migration; called only when ``should_run`` returns ``True``."""


class GatewaySpecificIndexFolder(Upgrader):
    """Migrate a flat ``.zk_chat_db`` directory to a per-gateway subdirectory layout."""

    def __init__(self, config: Config) -> None:
        """Store the vault config used to determine database and gateway paths."""
        self.config = config

    @property
    def db_dir(self) -> Path:
        """Absolute path to the vault's ``.zk_chat_db`` root directory."""
        return Path(self.config.vault) / ".zk_chat_db"

    @property
    def index_dir(self) -> Path:
        """Absolute path to the gateway-specific subdirectory inside ``db_dir``."""
        return self.db_dir / self.config.gateway.value

    @override
    def should_run(self) -> bool:
        """Return ``True`` when the db dir exists but the gateway-specific sub-directory does not."""
        if self.db_dir.exists():
            if not self.index_dir.exists():
                return True
        return False

    @override
    def run(self) -> None:
        """Move all non-gateway items from ``db_dir`` into ``index_dir`` to complete the migration."""
        sqlite_file = self.db_dir / "chroma.sqlite3"
        if not self.index_dir.exists() or sqlite_file.exists():
            self.index_dir.mkdir(parents=True, exist_ok=True)

            for item in self.db_dir.iterdir():
                if item.name not in [ModelGateway.OLLAMA.value, ModelGateway.OPENAI.value]:
                    shutil.move(str(item), str(self.index_dir / item.name))
