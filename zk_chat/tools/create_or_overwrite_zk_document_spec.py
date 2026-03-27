from unittest.mock import Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.models import ZkDocument
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument, prepare_document


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def mock_console_service():
    return Mock(spec=RichConsoleService)


@pytest.fixture
def write_tool(mock_filesystem, mock_console_service):
    mock_filesystem.get_directory_path.return_value = ""
    mock_filesystem.path_exists.return_value = True
    return CreateOrOverwriteZkDocument(DocumentService(mock_filesystem), mock_console_service)


class DescribePrepareDocument:
    """Tests for the prepare_document pure function."""

    def should_sanitize_title_for_filename(self):
        document = prepare_document('title<with>illegal*chars', "content")

        assert document.relative_path == "titlewithillegalchars.md"

    def should_add_md_extension_to_title(self):
        document = prepare_document("My Note", "content")

        assert document.relative_path == "My Note.md"

    def should_not_double_add_md_extension_when_already_present(self):
        document = prepare_document("My Note.md", "content")

        assert document.relative_path == "My Note.md"

    def should_add_reviewed_false_to_empty_metadata(self):
        document = prepare_document("title", "content")

        assert document.metadata == {"reviewed": False}

    def should_handle_none_metadata(self):
        document = prepare_document("title", "content", metadata=None)

        assert document.metadata == {"reviewed": False}

    def should_handle_non_dict_metadata(self):
        document = prepare_document("title", "content", metadata="not a dict")

        assert document.metadata == {"reviewed": False}

    def should_merge_provided_metadata_with_reviewed_flag(self):
        document = prepare_document("title", "content", metadata={"author": "Alice"})

        assert document.metadata == {"author": "Alice", "reviewed": False}

    def should_always_reset_reviewed_to_false_even_when_true_provided(self):
        """Newly written documents are always unreviewed regardless of supplied metadata."""
        document = prepare_document("title", "content", metadata={"reviewed": True})

        assert document.metadata["reviewed"] is False

    def should_return_zk_document_instance(self):
        document = prepare_document("title", "content")

        assert isinstance(document, ZkDocument)

    def should_set_content_on_document(self):
        document = prepare_document("title", "the body content")

        assert document.content == "the body content"


class DescribeCreateOrOverwriteZkDocument:
    """Tests for the CreateOrOverwriteZkDocument tool."""

    def should_write_document_with_dict_metadata(self, write_tool, mock_filesystem):
        title = "Path"
        metadata = {"title": "Test Document"}
        content = "# Test Content"

        result = write_tool.run(title=title, metadata=metadata, content=content)

        assert f"Successfully wrote to {title}.md" in result
        mock_filesystem.write_markdown.assert_called_once()
        call_args = mock_filesystem.write_markdown.call_args[0]
        assert call_args[0] == f"{title}.md"
        expected_metadata = metadata.copy()
        expected_metadata["reviewed"] = False
        assert call_args[1] == expected_metadata
        assert call_args[2] == content

    def should_write_document_with_default_metadata_when_none_provided(self, write_tool, mock_filesystem):
        title = "Path"
        content = "# Test Content"

        result = write_tool.run(title=title, metadata=None, content=content)

        assert f"Successfully wrote to {title}.md" in result
        mock_filesystem.write_markdown.assert_called_once()
        call_args = mock_filesystem.write_markdown.call_args[0]
        assert call_args[0] == f"{title}.md"
        assert call_args[1] == {"reviewed": False}
        assert call_args[2] == content

    def should_write_document_with_default_metadata_when_non_dict_provided(self, write_tool, mock_filesystem):
        title = "Path"
        content = "# Test Content"

        result = write_tool.run(title=title, metadata="This is not a dictionary", content=content)

        assert f"Successfully wrote to {title}.md" in result
        mock_filesystem.write_markdown.assert_called_once()
        call_args = mock_filesystem.write_markdown.call_args[0]
        assert call_args[0] == f"{title}.md"
        assert call_args[1] == {"reviewed": False}
        assert call_args[2] == content
