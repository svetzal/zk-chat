import os
from datetime import datetime
from pathlib import Path

from pytest import fixture

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway


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
    return MarkdownFilesystemGateway(str(temp_dir))


class DescribeMarkdownFilesystemGateway:
    """Integration tests for the MarkdownFilesystemGateway class."""

    def should_be_instantiated_with_root_path(self):
        root_path = "/some/path"

        gateway = MarkdownFilesystemGateway(root_path)

        assert isinstance(gateway, MarkdownFilesystemGateway)
        assert gateway.root_path == root_path

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