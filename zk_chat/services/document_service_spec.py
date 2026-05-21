"""
Tests for the DocumentService which handles document lifecycle operations in a Zettelkasten.
"""

import pytest

from zk_chat.models import ZkDocument
from zk_chat.services.document_service import DocumentService


class DescribeDocumentService:
    """Tests for the DocumentService component which handles document CRUD operations."""

    @pytest.fixture
    def document_service(self, mock_filesystem):
        return DocumentService(mock_filesystem)

    @pytest.fixture
    def sample_document(self):
        return ZkDocument(
            relative_path="test/document.md",
            metadata={"tags": ["test"], "author": "tester"},
            content="# Test Document\n\nThis is test content.",
        )

    @pytest.fixture
    def sample_metadata(self):
        return {"tags": ["test"], "author": "tester"}

    @pytest.fixture
    def sample_content(self):
        return "# Test Document\n\nThis is test content."

    def should_be_instantiated_with_filesystem_gateway(self, mock_filesystem):
        service = DocumentService(mock_filesystem)

        assert isinstance(service, DocumentService)
        assert service.filesystem_gateway == mock_filesystem

    def should_read_document_from_filesystem(self, document_service, mock_filesystem, sample_metadata, sample_content):
        test_path = "test/document.md"
        mock_filesystem.read_markdown.return_value = (sample_metadata, sample_content)

        result = document_service.read_document(test_path)

        mock_filesystem.read_markdown.assert_called_once_with(test_path)
        assert result.relative_path == test_path
        assert result.metadata == sample_metadata
        assert result.content == sample_content

    def should_write_document_to_filesystem(self, document_service, mock_filesystem, sample_document):
        mock_filesystem.get_directory_path.return_value = "test"
        mock_filesystem.path_exists.return_value = True

        document_service.write_document(sample_document)

        mock_filesystem.write_markdown.assert_called_once_with(
            sample_document.relative_path, sample_document.metadata, sample_document.content
        )

    def should_create_directory_when_writing_document_to_new_path(
        self, document_service, mock_filesystem, sample_document
    ):
        mock_filesystem.get_directory_path.return_value = "new_folder"
        mock_filesystem.path_exists.return_value = False

        document_service.write_document(sample_document)

        mock_filesystem.create_directory.assert_called_once_with("new_folder")
        mock_filesystem.write_markdown.assert_called_once()

    def should_delete_existing_document(self, document_service, mock_filesystem):
        test_path = "test/document.md"
        mock_filesystem.path_exists.return_value = True

        document_service.delete_document(test_path)

        mock_filesystem.delete_file.assert_called_once_with(test_path)

    def should_raise_error_when_deleting_nonexistent_document(self, document_service, mock_filesystem):
        test_path = "nonexistent.md"
        mock_filesystem.path_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            document_service.delete_document(test_path)

    def should_rename_existing_document(self, document_service, mock_filesystem):
        source_path = "old/path.md"
        target_path = "new/path.md"
        mock_filesystem.path_exists.return_value = True

        document_service.rename_document(source_path, target_path)

        mock_filesystem.rename_file.assert_called_once_with(source_path, target_path)

    def should_raise_error_when_renaming_nonexistent_document(self, document_service, mock_filesystem):
        source_path = "nonexistent.md"
        target_path = "new/path.md"
        mock_filesystem.path_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            document_service.rename_document(source_path, target_path)

    def should_list_all_document_paths(self, document_service, mock_filesystem):
        expected_paths = ["doc1.md", "folder/doc2.md", "folder/subfolder/doc3.md"]
        mock_filesystem.iterate_markdown_files.return_value = iter(expected_paths)

        result = document_service.list_documents()

        assert result == expected_paths

    def should_iterate_through_all_documents(self, document_service, mock_filesystem):
        paths = ["doc1.md", "doc2.md"]
        mock_filesystem.iterate_markdown_files.return_value = iter(paths)
        mock_filesystem.read_markdown.side_effect = [({"key": "value1"}, "Content 1"), ({"key": "value2"}, "Content 2")]

        results = list(document_service.iterate_documents())

        assert len(results) == 2
        assert results[0].relative_path == "doc1.md"
        assert results[1].relative_path == "doc2.md"

    def should_check_document_exists(self, document_service, mock_filesystem):
        mock_filesystem.path_exists.return_value = True

        result = document_service.document_exists("test.md")

        assert result is True
        mock_filesystem.path_exists.assert_called_once_with("test.md")

    def should_check_document_not_exists(self, document_service, mock_filesystem):
        mock_filesystem.path_exists.return_value = False

        result = document_service.document_exists("nonexistent.md")

        assert result is False

