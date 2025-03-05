import os
from datetime import datetime
from pathlib import Path

from pytest import fixture

from zk_chat.filesystem_gateway import FilesystemGateway


@fixture
def temp_dir(tmp_path):
    """Create a temporary directory with some test files."""
    # Create markdown files
    (tmp_path / "test1.md").write_text("test content 1")
    (tmp_path / "test2.md").write_text("test content 2")
    # Create a subdirectory with markdown files
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "test3.md").write_text("test content 3")
    # Create a non-markdown file
    (tmp_path / "test.txt").write_text("test content")
    return tmp_path


@fixture
def gateway(temp_dir):
    return FilesystemGateway(str(temp_dir))


class DescribeFilesystemGateway:
    """Integration tests for the FilesystemGateway class."""

    def should_be_instantiated_with_root_path(self):
        root_path = "/some/path"

        gateway = FilesystemGateway(root_path)

        assert isinstance(gateway, FilesystemGateway)
        assert gateway.root_path == root_path

    def should_join_paths(self, gateway):
        path1 = "path1"
        path2 = "path2"
        expected = os.path.join(path1, path2)

        result = gateway.join_paths(path1, path2)

        assert result == expected

    def should_check_if_path_exists(self, gateway, temp_dir):
        existing_path = str(temp_dir / "test1.md")
        non_existing_path = str(temp_dir / "non_existing.md")

        assert gateway.path_exists(existing_path) is True
        assert gateway.path_exists(non_existing_path) is False

    def should_get_modified_time(self, gateway, temp_dir):
        test_file = temp_dir / "test1.md"

        result = gateway.get_modified_time(str(test_file))

        assert isinstance(result, datetime)
        assert result == datetime.fromtimestamp(os.path.getmtime(str(test_file)))

    def should_get_directory_path(self, gateway, temp_dir):
        test_path = str(temp_dir / "subdir" / "test3.md")
        expected = "subdir"

        result = gateway.get_directory_path(test_path)

        assert result == expected

    def should_create_directory(self, gateway, temp_dir):
        new_dir = temp_dir / "new_dir" / "nested"

        gateway.create_directory(str(new_dir))

        assert new_dir.exists()
        assert new_dir.is_dir()

    def should_get_relative_path(self, gateway, temp_dir):
        full_path = str(temp_dir / "subdir" / "test3.md")
        expected = str(Path("subdir") / "test3.md")

        result = gateway.get_relative_path(full_path, str(temp_dir))

        assert result == expected

    def should_iterate_markdown_files(self, gateway, temp_dir):
        expected_files = {
            "test1.md",
            "test2.md",
            str(Path("subdir") / "test3.md")
        }

        found_files = set()
        for relative_path in gateway.iterate_markdown_files():
            found_files.add(relative_path)
            assert relative_path.endswith(".md")

        assert found_files == expected_files
