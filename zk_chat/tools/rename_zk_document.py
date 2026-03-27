import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.filename_utils import ensure_md_extension, sanitize_filename
from zk_chat.services.document_service import DocumentService

logger = structlog.get_logger()


class RenameZkDocument(LLMTool):
    def __init__(self, document_service: DocumentService):
        self.document_service = document_service

    def run(self, source_title: str, target_title: str) -> str:
        source_path = ensure_md_extension(sanitize_filename(source_title))
        target_path = ensure_md_extension(sanitize_filename(target_title))

        try:
            logger.info("renaming document", source_path=source_path, target_path=target_path)

            self.document_service.rename_document(source_path, target_path)

            return f"Successfully renamed document from '{source_path}' to '{target_path}'"
        except FileNotFoundError as e:
            error_message = f"Failed to rename document: {str(e)}"
            logger.error(error_message)
            return error_message
        except OSError as e:
            error_message = (
                f"Failed to rename document from '{source_path}' to '{target_path}': "
                f"{str(e)}. This could be due to insufficient permissions, "
                f"the target file already existing, or other filesystem issues."
            )
            logger.error(error_message)
            return error_message

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "rename_document",
                "description": "Change the name or path of an existing document in the Zettelkasten knowledge base. "
                "Use this when you need to reorganize the knowledge base or provide a more appropriate "
                "name for a document. This preserves the document's content while changing its "
                "identifier. Returns a success message if the rename operation succeeds, or a detailed "
                "error message if it fails.",
                "parameters": {
                    "type": "object",
                    "properties": {
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
                    "additionalProperties": False,
                    "required": ["source_title", "target_title"],
                },
            },
        }
