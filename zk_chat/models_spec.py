"""
Tests for domain models.
"""

from zk_chat.models import ZkDocument


class DescribeZkDocument:
    """Tests for the ZkDocument model."""

    class DescribeTitle:
        """Tests for the title property which derives a display name from the file path."""

        def should_return_filename_without_extension(self):
            doc = ZkDocument(relative_path="notes/my-note.md", metadata={}, content="")

            assert doc.title == "my-note"

        def should_strip_at_prefix_with_space(self):
            doc = ZkDocument(relative_path="notes/@ My Note.md", metadata={}, content="")

            assert doc.title == "My Note"

        def should_strip_exclamation_prefix_with_space(self):
            doc = ZkDocument(relative_path="notes/! Important Note.md", metadata={}, content="")

            assert doc.title == "Important Note"

        def should_strip_at_prefix_without_space(self):
            doc = ZkDocument(relative_path="@note.md", metadata={}, content="")

            assert doc.title == "note"

        def should_strip_exclamation_prefix_without_space(self):
            doc = ZkDocument(relative_path="!urgent.md", metadata={}, content="")

            assert doc.title == "urgent"

        def should_handle_nested_paths(self):
            doc = ZkDocument(relative_path="vault/subfolder/deep/note.md", metadata={}, content="")

            assert doc.title == "note"

        def should_use_only_basename_not_directory_components(self):
            doc = ZkDocument(relative_path="@ prefix/my-note.md", metadata={}, content="")

            assert doc.title == "my-note"

        def should_not_strip_at_in_middle_of_name(self):
            doc = ZkDocument(relative_path="user@host.md", metadata={}, content="")

            assert doc.title == "user@host"

        def should_not_strip_exclamation_in_middle_of_name(self):
            doc = ZkDocument(relative_path="hello!world.md", metadata={}, content="")

            assert doc.title == "hello!world"

    class DescribeId:
        """Tests for the id property which returns the full relative path."""

        def should_return_relative_path(self):
            doc = ZkDocument(relative_path="notes/test.md", metadata={}, content="")

            assert doc.id == "notes/test.md"

        def should_preserve_nested_path_structure(self):
            doc = ZkDocument(relative_path="vault/a/b/c/deep.md", metadata={}, content="")

            assert doc.id == "vault/a/b/c/deep.md"
