"""Service for gathering vault filesystem statistics."""

import os

from pydantic import BaseModel

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway


class DbInfo(BaseModel):
    location: str
    total_size: int
    file_count: int


class VaultStatusService:
    """Provides filesystem statistics about a vault and its index database."""

    def __init__(self, filesystem_gateway: MarkdownFilesystemGateway) -> None:
        self._filesystem_gateway = filesystem_gateway

    def count_markdown_files(self) -> int:
        """Count the number of markdown files in the vault."""
        return sum(1 for _ in self._filesystem_gateway.iterate_markdown_files())

    def get_db_info(self, vault_path: str) -> DbInfo | None:
        """Return size and file count for the ChromaDB directory, or None if absent."""
        db_dir = os.path.join(vault_path, ".zk_chat_db")
        if not os.path.exists(db_dir):
            return None
        total_size = 0
        file_count = 0
        for dirpath, _dirnames, filenames in os.walk(db_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
                file_count += 1
        return DbInfo(location=db_dir, total_size=total_size, file_count=file_count)
