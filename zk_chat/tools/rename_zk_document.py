import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.filename_utils import ensure_md_extension, sanitize_filename
from zk_chat.services.document_service import DocumentService
from zk_chat.services.index_service import IndexService
from zk_chat.tools.tool_helpers import build_descriptor, tool_boundary

logger = structlog.get_logger()


def _rename_error_prefix(self, source_title, target_title):
    src = ensure_md_extension(sanitize_filename(source_title))
    tgt = ensure_md_extension(sanitize_filename(target_title))
    return f"Failed to rename document from '{src}' to '{tgt}'"


class RenameZkDocument(LLMTool):
    """LLM tool that renames a document in the vault and updates the search index."""

    def __init__(self, document_service: DocumentService, index_service: IndexService) -> None:
        """Store the document service and index service used during rename operations."""
        self.document_service = document_service
        self.index_service = index_service

    @tool_boundary(OSError, _rename_error_prefix)
    def run(self, source_title: str, target_title: str) -> str:
        """Rename a document from ``source_title`` to ``target_title``, updating the index."""
        source_path = ensure_md_extension(sanitize_filename(source_title))
        target_path = ensure_md_extension(sanitize_filename(target_title))
        logger.info("renaming document", source_path=source_path, target_path=target_path)
        self.document_service.rename_document(source_path, target_path)
        self.index_service.remove_document_from_index(source_path)
        self.index_service.index_document(target_path)
        return f"Successfully renamed document from '{source_path}' to '{target_path}'"

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``rename_document`` tool."""
        return build_descriptor(
            name="rename_document",
            description="Change the name or path of an existing document in the Zettelkasten knowledge base. "
            "Use this when you need to reorganize the knowledge base or provide a more appropriate "
            "name for a document. This preserves the document's content while changing its "
            "identifier. Returns a success message if the rename operation succeeds, or a detailed "
            "error message if it fails.",
            properties={
                "source_title": {
                    "type": "string",
                    "description": "The title or relative path of the document to rename. The .md extension "
                    "is optional.",
                },
                "target_title": {
                    "type": "string",
                    "description": "The new title or relative path for the document. The .md extension is "
                    "optional.",
                },
            },
            required=["source_title", "target_title"],
            additional_properties=False,
        )
