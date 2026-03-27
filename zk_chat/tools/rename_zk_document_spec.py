from unittest.mock import Mock

import pytest

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.rename_zk_document import RenameZkDocument


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def tool(mock_filesystem) -> RenameZkDocument:
    return RenameZkDocument(DocumentService(mock_filesystem))


class DescribeRenameZkDocument:
    """
    Tests for the RenameZkDocument tool which handles renaming Zettelkasten documents.

    Sanitization and extension logic are tested in filename_utils_spec.py.
    """

    def should_be_instantiated_with_document_service(self, mock_filesystem):
        document_service = DocumentService(mock_filesystem)
        tool = RenameZkDocument(document_service)

        assert isinstance(tool, RenameZkDocument)
        assert tool.document_service is document_service

    def should_rename_document_successfully(self, tool: RenameZkDocument, mock_filesystem):
        source_title = "source_document"
        target_title = "target_document"
        source_path = "source_document.md"
        target_path = "target_document.md"

        mock_filesystem.path_exists.return_value = True

        result = tool.run(source_title, target_title)

        mock_filesystem.rename_file.assert_called_once_with(source_path, target_path)
        assert f"Successfully renamed document from '{source_path}' to '{target_path}'" in result

    def should_handle_file_not_found_error(self, tool: RenameZkDocument, mock_filesystem):
        source_title = "nonexistent_document"
        target_title = "target_document"
        source_path = "nonexistent_document.md"

        mock_filesystem.path_exists.return_value = False

        result = tool.run(source_title, target_title)

        assert "Failed to rename document" in result
        assert source_path in result

    def should_handle_os_error(self, tool: RenameZkDocument, mock_filesystem):
        source_title = "source_document"
        target_title = "target_document"
        source_path = "source_document.md"
        target_path = "target_document.md"

        mock_filesystem.path_exists.return_value = True
        error_message = "Permission denied"
        mock_filesystem.rename_file.side_effect = OSError(error_message)

        result = tool.run(source_title, target_title)

        assert f"Failed to rename document from '{source_path}' to '{target_path}'" in result
        assert error_message in result
