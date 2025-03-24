import pytest
from pytest_mock import MockerFixture

from zk_chat.models import ZkDocument
from zk_chat.tools.rename_zk_document import RenameZkDocument
from zk_chat.zettelkasten import Zettelkasten


@pytest.fixture
def mock_zk(mocker: MockerFixture) -> Zettelkasten:
    return mocker.Mock(spec=Zettelkasten)


@pytest.fixture
def tool(mock_zk: Zettelkasten) -> RenameZkDocument:
    return RenameZkDocument(mock_zk)


class DescribeRenameZkDocument:
    """
    Tests for the RenameZkDocument tool which handles renaming Zettelkasten documents
    """
    def should_be_instantiated_with_zettelkasten(self, mock_zk: Zettelkasten):
        tool = RenameZkDocument(mock_zk)

        assert isinstance(tool, RenameZkDocument)
        assert tool.zk == mock_zk

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

    def should_rename_document_successfully(self, tool: RenameZkDocument, mock_zk: Zettelkasten):
        source_title = 'source_document'
        target_title = 'target_document'
        source_path = 'source_document.md'
        target_path = 'target_document.md'
        
        # Set up the mock to return a document when rename_document is called
        renamed_document = ZkDocument(
            relative_path=target_path,
            content="Document Content",
            metadata={},
        )
        mock_zk.rename_document.return_value = renamed_document

        # Call the tool's run method
        result = tool.run(source_title, target_title)

        # Verify the mock was called with the correct arguments
        mock_zk.rename_document.assert_called_once_with(source_path, target_path)
        
        # Verify the result is a success message
        assert f"Successfully renamed document from '{source_path}' to '{target_path}'" in result

    def should_handle_file_not_found_error(self, tool: RenameZkDocument, mock_zk: Zettelkasten):
        source_title = 'nonexistent_document'
        target_title = 'target_document'
        source_path = 'nonexistent_document.md'
        
        # Set up the mock to raise FileNotFoundError when rename_document is called
        error_message = f"Source document {source_path} does not exist"
        mock_zk.rename_document.side_effect = FileNotFoundError(error_message)

        # Call the tool's run method
        result = tool.run(source_title, target_title)

        # Verify the result is an error message
        assert "Failed to rename document" in result
        assert error_message in result

    def should_handle_os_error(self, tool: RenameZkDocument, mock_zk: Zettelkasten):
        source_title = 'source_document'
        target_title = 'target_document'
        source_path = 'source_document.md'
        target_path = 'target_document.md'
        
        # Set up the mock to raise OSError when rename_document is called
        error_message = "Permission denied"
        mock_zk.rename_document.side_effect = OSError(error_message)

        # Call the tool's run method
        result = tool.run(source_title, target_title)

        # Verify the result is an error message
        assert f"Failed to rename document from '{source_path}' to '{target_path}'" in result
        assert error_message in result