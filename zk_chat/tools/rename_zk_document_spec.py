import pytest

from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.rename_zk_document import RenameZkDocument


@pytest.fixture
def tool(mock_filesystem, make_index_service) -> RenameZkDocument:
    index_service = make_index_service(filesystem=mock_filesystem)
    index_service.tokenizer_gateway.encode.return_value = [1, 2, 3]
    index_service.tokenizer_gateway.decode.return_value = "decoded"
    return RenameZkDocument(DocumentService(mock_filesystem), index_service)


class DescribeRenameZkDocument:
    """
    Tests for the RenameZkDocument tool which handles renaming Zettelkasten documents.

    Sanitization and extension logic are tested in filename_utils_spec.py.
    """

    def should_be_instantiated_with_document_service(self, mock_filesystem, make_index_service):
        document_service = DocumentService(mock_filesystem)
        index_service = make_index_service(filesystem=mock_filesystem)
        tool = RenameZkDocument(document_service, index_service)

        assert isinstance(tool, RenameZkDocument)
        assert tool.document_service is document_service
        assert tool.index_service is index_service

    def should_rename_document_successfully(self, tool: RenameZkDocument, mock_filesystem):
        source_title = "source_document"
        target_title = "target_document"
        source_path = "source_document.md"
        target_path = "target_document.md"

        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({"title": "Target"}, "content body")

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

    def should_purge_old_index_entries_and_reindex_under_new_path(
        self, mock_filesystem, mock_chroma_documents, mock_chroma_excerpts, make_index_service
    ):
        index_service = make_index_service(
            chroma_excerpts=mock_chroma_excerpts,
            chroma_documents=mock_chroma_documents,
            filesystem=mock_filesystem,
        )
        index_service.tokenizer_gateway.encode.return_value = [1, 2, 3]
        index_service.tokenizer_gateway.decode.return_value = "decoded"
        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({"title": "Target"}, "content body")
        tool = RenameZkDocument(DocumentService(mock_filesystem), index_service)

        tool.run("source_document", "target_document")

        mock_chroma_documents.delete_items.assert_called_once_with(
            collection_name=ZkCollectionName.DOCUMENTS, where={"id": "source_document.md"}
        )
        mock_chroma_excerpts.delete_items.assert_any_call(
            collection_name=ZkCollectionName.EXCERPTS, where={"document_path": "source_document.md"}
        )
        add_docs_call = mock_chroma_documents.add_items.call_args
        assert add_docs_call.kwargs["ids"] == ["target_document.md"]
        assert add_docs_call.kwargs["metadatas"][0]["id"] == "target_document.md"
        mock_chroma_excerpts.add_items.assert_called_once()

    def should_make_renamed_document_findable_under_new_path(
        self, mock_filesystem, mock_chroma_documents, make_index_service
    ):
        mock_chroma_documents.query.return_value = {
            "ids": [["target_document.md"]],
            "documents": [["content body"]],
            "metadatas": [[{"id": "target_document.md", "title": "Target"}]],
            "distances": [[0.3]],
        }
        index_service = make_index_service(chroma_documents=mock_chroma_documents, filesystem=mock_filesystem)
        index_service.tokenizer_gateway.encode.return_value = [1, 2, 3]
        index_service.tokenizer_gateway.decode.return_value = "decoded"
        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({"title": "Target"}, "content body")
        tool = RenameZkDocument(DocumentService(mock_filesystem), index_service)

        tool.run("source_document", "target_document")
        results = index_service.query_documents("content body")

        assert results[0].document.relative_path == "target_document.md"
