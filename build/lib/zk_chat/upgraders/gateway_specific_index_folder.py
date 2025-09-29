import os
import shutil
from pathlib import Path
from typing import override

from zk_chat.config import Config, ModelGateway


class Upgrader:
    def should_run(self) -> bool:
        return False

    def run(self):
        pass


class GatewaySpecificIndexFolder(Upgrader):

    def __init__(self, config: Config):
        self.config = config

    @property
    def db_dir(self):
        return Path(self.config.vault) / ".zk_chat_db"

    @property
    def index_dir(self):
        return self.db_dir / self.config.gateway.value

    @override
    def should_run(self) -> bool:
        if self.db_dir.exists():
            if not self.index_dir.exists():
                return True
        return False

    @override
    def run(self):
        sqlite_file = self.db_dir / "chroma.sqlite3"
        if not self.index_dir.exists() or sqlite_file.exists():
            self.index_dir.mkdir(parents=True, exist_ok=True)

            for item in self.db_dir.iterdir():
                if item.name not in [ModelGateway.OLLAMA.value, ModelGateway.OPENAI.value]:
                    shutil.move(str(item), str(self.index_dir / item.name))
