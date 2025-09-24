from typing import Optional

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class RenameZkDocument(LLMTool):
    def __init__(self, zk: Zettelkasten, console_service: RichConsoleService = None):
        self.zk = zk
        self.console_service = console_service or RichConsoleService()

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a relative path across operating systems.
        Replaces spaces with underscores and removes characters not allowed in relative paths.
        """
        import re
        sanitized = filename.strip()
        sanitized = re.sub(r'[\\/*?:"<>|]', '', sanitized)
        return sanitized

    def _ensure_md_extension(self, path: str) -> str:
        """
        Ensure the path has a .md extension.
        """
        if not path.endswith(".md"):
            path += ".md"
        return path

    def run(self, source_title: str, target_title: str) -> str:
        # Sanitize and ensure .md extension for source and target
        source_path = self._ensure_md_extension(self._sanitize_filename(source_title))
        target_path = self._ensure_md_extension(self._sanitize_filename(target_title))

        try:
            logger.info("renaming document", source_path=source_path, target_path=target_path)

            # Rename the document
            renamed_document = self.zk.rename_document(source_path, target_path)

            return f"Successfully renamed document from '{source_path}' to '{target_path}'"
        except FileNotFoundError as e:
            error_message = f"Failed to rename document: {str(e)}"
            logger.error(error_message)
            return error_message
        except OSError as e:
            error_message = f"Failed to rename document from '{source_path}' to '{target_path}': {str(e)}. This could be due to insufficient permissions, the target file already existing, or other filesystem issues."
            logger.error(error_message)
            return error_message

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "rename_document",
                "description": "Change the name or path of an existing document in the Zettelkasten knowledge base. Use this when you need to reorganize the knowledge base or provide a more appropriate name for a document. This preserves the document's content while changing its identifier. Returns a success message if the rename operation succeeds, or a detailed error message if it fails.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_title": {
                            "type": "string",
                            "description": "The title or relative path of the document to rename. The .md extension is optional."
                        },
                        "target_title": {
                            "type": "string",
                            "description": "The new title or relative path for the document. The .md extension is optional."
                        }
                    },
                    "additionalProperties": False,
                    "required": ["source_title", "target_title"]
                },
            },
        }
