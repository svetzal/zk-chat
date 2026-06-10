import os
from collections.abc import Iterator
from datetime import datetime
from typing import Any

import structlog

logger = structlog.get_logger()


class FilesystemGateway:
    """Gateway for filesystem operations to abstract OS dependencies."""

    def __init__(self, root_path: str) -> None:
        """Anchor all path operations to ``root_path`` as the vault root."""
        self.root_path = root_path

    def join_paths(self, *paths: str) -> str:
        """Join path components using the OS separator, delegating to ``os.path.join``."""
        return os.path.join(*paths)

    def path_exists(self, relative_path: str) -> bool:
        """Return ``True`` if the file or directory at ``relative_path`` exists on disk."""
        full_path = self._get_full_path(relative_path)
        return os.path.exists(full_path)

    def get_modified_time(self, relative_path: str) -> datetime:
        """Return the last-modified ``datetime`` for the file at ``relative_path``."""
        full_path = self._get_full_path(relative_path)
        return datetime.fromtimestamp(os.path.getmtime(full_path))

    def get_directory_path(self, relative_path: str) -> str:
        """Return the relative directory path containing the file at ``relative_path``."""
        full_path = self._get_full_path(relative_path)
        full_dir_path = os.path.dirname(full_path)
        return self._get_relative_path(full_dir_path)

    def create_directory(self, relative_path: str) -> None:
        """Create the directory at ``relative_path`` (and any missing parents) inside the vault."""
        full_path = self._get_full_path(relative_path)
        os.makedirs(full_path)

    def _get_relative_path(self, absolute_path: str) -> str:
        return os.path.relpath(absolute_path, self.root_path)

    def _get_full_path(self, relative_path: str) -> str:
        return self.join_paths(self.root_path, relative_path)

    def read_file(self, relative_path: str) -> str:
        """Read and return the full text content of the file at ``relative_path``."""
        full_path = self._get_full_path(relative_path)
        with open(full_path) as f:
            return f.read()

    def write_file(self, relative_path: str, content: str) -> None:
        """Write ``content`` to the file at ``relative_path``, creating or replacing it."""
        logger.debug("Writing file", path=relative_path)
        full_path = self._get_full_path(relative_path)
        with open(full_path, "w") as f:
            f.write(content)

    def rename_file(self, source_path: str, target_path: str) -> None:
        """Creates target directory if it does not exist."""
        import os

        logger.debug("Renaming file", source=source_path, target=target_path)
        full_source_path = self._get_full_path(source_path)
        full_target_path = self._get_full_path(target_path)

        target_dir = os.path.dirname(full_target_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        os.rename(full_source_path, full_target_path)

    def delete_file(self, relative_path: str) -> None:
        """Raises FileNotFoundError explicitly rather than propagating the OS error."""
        import os

        full_path = self._get_full_path(relative_path)

        if not os.path.exists(full_path):
            logger.warning("File not found during delete", path=relative_path)
            raise FileNotFoundError(f"File {relative_path} does not exist")

        logger.debug("Deleting file", path=relative_path)
        os.remove(full_path)

    def get_absolute_path_for_tool_access(self, relative_path: str) -> str:
        """Returns absolute path for tools needing to pass paths to external libraries (e.g. image analysis).

        Raises ValueError if the path attempts directory traversal outside the vault.
        """
        # Ensure the path doesn't escape the sandbox
        if ".." in relative_path or relative_path.startswith("/"):
            raise ValueError(f"Invalid path: {relative_path}")

        return self._get_full_path(relative_path)

    def iterate_files_by_extensions(self, extensions: list[str]) -> Iterator[str]:
        """Yield relative paths for every file under ``root_path`` whose extension is in ``extensions``."""
        import os

        for root, _dirs, files in os.walk(self.root_path):
            for file in files:
                _, ext = os.path.splitext(file)
                if ext.lower().lstrip(".") in [e.lower().lstrip(".") for e in extensions]:
                    full_path = os.path.join(root, file)
                    yield self._get_relative_path(full_path)

    def _walk_filesystem(self) -> Iterator[tuple[str, list[Any], list[str]]]:
        import os

        return os.walk(self.root_path)
