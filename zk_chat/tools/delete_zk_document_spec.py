from unittest.mock import Mock

import pytest

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.chroma_gateway import ChromaGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.delete_zk_document import DeleteZkDocument


@pytest.fixture
def delete_tool(mock_filesystem, mock_console_gateway, make_index_service):
    return DeleteZkDocument(
        DocumentService(mock_filesystem),
        make_index_service(filesystem=mock_filesystem),
        mock_console_gateway,
    )


class DescribeDeleteZkDocument:
    """Tests for the DeleteZkDocument tool."""

    def should_be_instantiated_with_document_service(self, mock_filesystem, mock_console_gateway, make_index_service):
        document_service = DocumentService(mock_filesystem)
        index_service = make_index_service()

        tool = DeleteZkDocument(document_service, index_service, mock_console_gateway)

        assert isinstance(tool, DeleteZkDocument)
        assert tool.document_service is document_service

    def should_delete_document_and_confirm_when_exists(self, delete_tool, mock_filesystem):
        relative_path = "test/path.md"
        mock_filesystem.path_exists.return_value = True

        result = delete_tool.run(relative_path=relative_path)

        # path_exists is called twice: once in tool.run() and once in DocumentService.delete_document()
        assert mock_filesystem.path_exists.call_count == 2
        mock_filesystem.delete_file.assert_called_once_with(relative_path)
        assert result == f"Document successfully deleted at {relative_path}"

    def should_return_not_found_message_when_document_missing(self, delete_tool, mock_filesystem):
        relative_path = "test/nonexistent.md"
        mock_filesystem.path_exists.return_value = False

        result = delete_tool.run(relative_path=relative_path)

        mock_filesystem.path_exists.assert_called_once_with(relative_path)
        mock_filesystem.delete_file.assert_not_called()
        assert result == f"Document not found at {relative_path}"

    def should_return_error_message_when_deletion_raises_os_error(self, delete_tool, mock_filesystem):
        relative_path = "test/error.md"
        mock_filesystem.path_exists.return_value = True
        mock_filesystem.delete_file.side_effect = OSError("Test error")

        result = delete_tool.run(relative_path=relative_path)

        # path_exists is called twice: once in tool.run() and once in DocumentService.delete_document()
        assert mock_filesystem.path_exists.call_count == 2
        mock_filesystem.delete_file.assert_called_once_with(relative_path)
        assert result == f"Error deleting document at {relative_path}: Test error"

    def should_remove_document_from_index_after_deleting_file(
        self, mock_filesystem, mock_console_gateway, make_index_service
    ):
        mock_chroma_excerpts = Mock(spec=ChromaGateway)
        mock_chroma_documents = Mock(spec=ChromaGateway)
        index_service = make_index_service(
            chroma_excerpts=mock_chroma_excerpts,
            chroma_documents=mock_chroma_documents,
            filesystem=mock_filesystem,
        )
        tool = DeleteZkDocument(DocumentService(mock_filesystem), index_service, mock_console_gateway)
        mock_filesystem.path_exists.return_value = True

        tool.run(relative_path="test/doc.md")

        mock_chroma_documents.delete_items.assert_called_once_with(
            collection_name=ZkCollectionName.DOCUMENTS,
            where={"id": "test/doc.md"},
        )
        mock_chroma_excerpts.delete_items.assert_called_once_with(
            collection_name=ZkCollectionName.EXCERPTS,
            where={"document_path": "test/doc.md"},
        )

    def should_have_correct_descriptor(self, delete_tool):
        descriptor = delete_tool.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "delete_document"
        assert "description" in descriptor["function"]
        assert descriptor["function"]["parameters"]["type"] == "object"
        assert "relative_path" in descriptor["function"]["parameters"]["properties"]
        assert descriptor["function"]["parameters"]["required"] == ["relative_path"]
