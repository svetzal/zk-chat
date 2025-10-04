import os
from datetime import datetime
from typing import Iterator, List


class FilesystemGateway:
    """Gateway for filesystem operations to abstract OS dependencies."""

    def __init__(self, root_path: str):
        """Initialize the gateway with a root path.

        Args:
            root_path: The root path for all filesystem operations
        """
        self.root_path = root_path

    def join_paths(self, *paths: str) -> str:
        """Join path components.

        Args:
            *paths: Path components to join

        Returns:
            str: Joined path
        """
        return os.path.join(*paths)

    def path_exists(self, relative_path: str) -> bool:
        """Check if a path exists.

        Args:
            relative_path: Relative path to check

        Returns:
            bool: True if path exists, False otherwise
        """
        full_path = self.get_full_path(relative_path)
        return os.path.exists(full_path)

    def get_modified_time(self, relative_path: str) -> datetime:
        """Get the last modified time of a file.

        Args:
            relative_path: Relative path to the file

        Returns:
            datetime: Last modified time
        """
        full_path = self.get_full_path(relative_path)
        return datetime.fromtimestamp(os.path.getmtime(full_path))

    def get_directory_path(self, relative_path: str) -> str:
        """Get the directory path of a file path.

        Args:
            relative_path: Relative path to get directory from

        Returns:
            str: Relative path to the directory
        """
        full_path = self.get_full_path(relative_path)
        full_dir_path = os.path.dirname(full_path)
        return self.get_relative_path(full_dir_path, self.root_path)

    def create_directory(self, relative_path: str) -> None:
        """Create a directory and all necessary parent directories.

        Args:
            relative_path: Relative path to create
        """
        full_path = self.get_full_path(relative_path)
        os.makedirs(full_path)

    def get_relative_path(self, path: str, start: str) -> str:
        """Get a relative path from a full path.

        Args:
            path: Path to convert to relative
            start: Start path to make relative to

        Returns:
            str: Relative path
        """
        return os.path.relpath(path, start)

    def get_full_path(self, relative_path: str) -> str:
        """Convert a relative path to a full path using the root path.

        Args:
            relative_path: Path relative to the root path

        Returns:
            str: Full path
        """
        return self.join_paths(self.root_path, relative_path)

    def read_file(self, relative_path: str) -> str:
        """Read content from a file.

        Args:
            relative_path: Relative path to the file

        Returns:
            str: Content of the file
        """
        full_path = self.get_full_path(relative_path)
        with open(full_path, "r") as f:
            return f.read()

    def write_file(self, relative_path: str, content: str) -> None:
        """Write content to a file.

        Args:
            relative_path: Relative path to the file
            content: Content to write
        """
        full_path = self.get_full_path(relative_path)
        with open(full_path, "w") as f:
            f.write(content)

    def rename_file(self, source_path: str, target_path: str) -> None:
        """Rename a file from source path to target path.

        Args:
            source_path: Relative source path of the file to rename
            target_path: Relative target path for the renamed file

        Raises:
            OSError: If there are filesystem-related errors (permissions, file not found, etc.)
        """
        import os
        full_source_path = self.get_full_path(source_path)
        full_target_path = self.get_full_path(target_path)

        # Create target directory if it doesn't exist
        target_dir = os.path.dirname(full_target_path)
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        os.rename(full_source_path, full_target_path)

    def delete_file(self, relative_path: str) -> None:
        """Delete a file at the specified path.

        Args:
            relative_path: Relative path to the file to delete

        Raises:
            FileNotFoundError: If the file doesn't exist
            OSError: If there are filesystem-related errors (permissions, etc.)
        """
        import os
        full_path = self.get_full_path(relative_path)

        if not os.path.exists(full_path):
            raise FileNotFoundError(f"File {relative_path} does not exist")

        os.remove(full_path)

    def iterate_files_by_extensions(self, extensions: List[str]) -> Iterator[str]:
        """Iterate through all files matching the given extensions.

        Args:
            extensions: List of file extensions to match (e.g., ['.md', '.txt'])

        Yields:
            str: Relative path for each matching file
        """
        for root, _, files in self._walk_filesystem():
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    full_path = self.join_paths(root, file)
                    relative_path = self.get_relative_path(full_path, self.root_path)
                    yield relative_path

    def _walk_filesystem(self):
        """Wrapper for os.walk to make it easier to mock in tests."""
        import os
        return os.walk(self.root_path)
