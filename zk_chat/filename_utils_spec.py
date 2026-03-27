"""Tests for the filename_utils module."""

import pytest

from zk_chat.filename_utils import ensure_md_extension, sanitize_filename


class DescribeSanitizeFilename:
    """Tests for the sanitize_filename pure function."""

    def should_return_plain_name_unchanged(self):
        result = sanitize_filename("my_document")

        assert result == "my_document"

    def should_strip_leading_and_trailing_whitespace(self):
        result = sanitize_filename("  my document  ")

        assert result == "my document"

    def should_remove_backslash(self):
        result = sanitize_filename("path\\name")

        assert result == "pathname"

    def should_remove_forward_slash(self):
        result = sanitize_filename("path/name")

        assert result == "pathname"

    def should_remove_asterisk(self):
        result = sanitize_filename("file*name")

        assert result == "filename"

    def should_remove_question_mark(self):
        result = sanitize_filename("file?name")

        assert result == "filename"

    def should_remove_colon(self):
        result = sanitize_filename("file:name")

        assert result == "filename"

    def should_remove_double_quote(self):
        result = sanitize_filename('file"name')

        assert result == "filename"

    def should_remove_less_than(self):
        result = sanitize_filename("file<name")

        assert result == "filename"

    def should_remove_greater_than(self):
        result = sanitize_filename("file>name")

        assert result == "filename"

    def should_remove_pipe(self):
        result = sanitize_filename("file|name")

        assert result == "filename"

    def should_remove_multiple_illegal_characters(self):
        result = sanitize_filename('test/file*name?.md')

        assert result == "testfilename.md"

    def should_preserve_spaces_within_name(self):
        result = sanitize_filename("My Document Title")

        assert result == "My Document Title"

    def should_preserve_hyphens_and_underscores(self):
        result = sanitize_filename("my-document_title")

        assert result == "my-document_title"

    def should_handle_empty_string(self):
        result = sanitize_filename("")

        assert result == ""


class DescribeEnsureMdExtension:
    """Tests for the ensure_md_extension pure function."""

    def should_add_md_extension_when_missing(self):
        result = ensure_md_extension("my_document")

        assert result == "my_document.md"

    def should_not_add_md_extension_when_already_present(self):
        result = ensure_md_extension("my_document.md")

        assert result == "my_document.md"

    def should_handle_path_with_subdirectory(self):
        result = ensure_md_extension("notes/my_document")

        assert result == "notes/my_document.md"

    def should_not_double_add_md_when_already_present_with_path(self):
        result = ensure_md_extension("notes/my_document.md")

        assert result == "notes/my_document.md"

    def should_handle_empty_string(self):
        result = ensure_md_extension("")

        assert result == ".md"

    @pytest.mark.parametrize("ext", [".txt", ".rst", ".html"])
    def should_add_md_extension_when_other_extension_present(self, ext: str):
        result = ensure_md_extension(f"document{ext}")

        assert result == f"document{ext}.md"
