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
    Tests for the RenameZkDocument tool which handles renaming Zettelkasten documents
    """

    def should_be_instantiated_with_document_service(self, mock_filesystem):
        document_service = DocumentService(mock_filesystem)
        tool = RenameZkDocument(document_service)

        assert isinstance(tool, RenameZkDocument)
        assert tool.document_service is document_service

    def should_sanitize_filename(self, tool: RenameZkDocument):
        filename = 'test/file*name?.md'

        sanitized = tool._sanitize_filename(filename)

        assert sanitized == 'testfilename.md'

    def should_ensure_md_extension(self, tool: RenameZkDocument):
        filename_without_extension = 'test_file'
        filename_with_extension = 'test_file.md'

        result_without_extension = tool._ensure_md_extension(filename_without_extension)
        result_with_extension = tool._ensure_md_extension(filename_with_extension)

        assert result_without_extension == 'test_file.md'
        assert result_with_extension == 'test_file.md'

    def should_rename_document_successfully(self, tool: RenameZkDocument, mock_filesystem):
        source_title = 'source_document'
        target_title = 'target_document'
        source_path = 'source_document.md'
        target_path = 'target_document.md'

        # Set up the mock filesystem
        mock_filesystem.path_exists.return_value = True

        # Call the tool's run method
        result = tool.run(source_title, target_title)

        # Verify the mock was called with the correct arguments
        mock_filesystem.rename_file.assert_called_once_with(source_path, target_path)

        # Verify the result is a success message
        assert f"Successfully renamed document from '{source_path}' to '{target_path}'" in result

    def should_handle_file_not_found_error(self, tool: RenameZkDocument, mock_filesystem):
        source_title = 'nonexistent_document'
        target_title = 'target_document'
        source_path = 'nonexistent_document.md'

        # Set up the mock to return False for document existence
        mock_filesystem.path_exists.return_value = False

        # Call the tool's run method
        result = tool.run(source_title, target_title)

        # Verify the result is an error message
        assert "Failed to rename document" in result
        assert source_path in result

    def should_handle_os_error(self, tool: RenameZkDocument, mock_filesystem):
        source_title = 'source_document'
        target_title = 'target_document'
        source_path = 'source_document.md'
        target_path = 'target_document.md'

        # Set up the mock to exist but raise OSError on rename
        mock_filesystem.path_exists.return_value = True
        error_message = "Permission denied"
        mock_filesystem.rename_file.side_effect = OSError(error_message)

        # Call the tool's run method
        result = tool.run(source_title, target_title)

        # Verify the result is an error message
        assert f"Failed to rename document from '{source_path}' to '{target_path}'" in result
        assert error_message in result
