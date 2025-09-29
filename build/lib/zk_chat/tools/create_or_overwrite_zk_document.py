from typing import Optional, Any

import structlog
import yaml
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.models import ZkDocument
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class CreateOrOverwriteZkDocument(LLMTool):
    def __init__(self, zk: Zettelkasten, console_service: RichConsoleService = None):
        self.zk = zk
        self.console_service = console_service or RichConsoleService()

    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitize a string to be used as a filename across operating systems.
        Replaces spaces with underscores and removes characters not allowed in filenames.
        """
        import re
        sanitized = filename.strip()
        sanitized = re.sub(r'[\\/*?:"<>|]', '', sanitized)
        return sanitized

    def run(self, title: str, content: str, metadata: Optional[dict[str, Any]] = None) -> str:
        relative_path = f"{self._sanitize_filename(title)}"
        if not relative_path.endswith(".md"):
            relative_path += ".md"
        self.console_service.print(f"[tool.info]Writing document at {relative_path}[/]")
        try:
            # Use metadata only if it's a dictionary, otherwise use empty dict
            base_metadata = {} if metadata is None or not isinstance(metadata, dict) else metadata
            # Merge with {"reviewed": False}
            augmented_metadata = base_metadata | {"reviewed": False}
            logger.info("writing file", relative_path=relative_path, metadata=augmented_metadata, content=content)
            document = ZkDocument(relative_path=relative_path, metadata=augmented_metadata, content=content)
            self.zk.create_or_overwrite_document(document)
            return f"Successfully wrote to {document.relative_path}\n{document.model_dump_json()}"
        except OSError as e:
            error_message = f"Failed to write document to {relative_path}: {str(e)}. This could be due to insufficient permissions, disk space issues, or the directory being read-only."
            logger.error(error_message)
            return error_message
        except yaml.YAMLError as e:
            error_message = f"Failed to serialize metadata for document {relative_path}: {str(e)}. Please check if the metadata contains valid YAML content."
            logger.error(error_message)
            return error_message

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "create_or_overwrite_document",
                "description": "Create a new document or update an existing document in the Zettelkasten knowledge base. Use this when you need to add new information to the knowledge base or update existing information. This tool will create a new document if the title doesn't exist, or completely replace the content of an existing document. Returns a success message with the document details if successful, or an error message if the operation fails.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the document"
                        },
                        "content": {
                            "type": "string",
                            "description": "The body content for the document. DO NOT INCLUDE FRONT-MATTER OR TITLE. Content should be in markdown format, with proper unescaped newline characters"
                        },
                        "metadata": {
                            "type": "object",
                            "description": "The metadata for the document in JSON format. If not provided, the metadata will be empty.",
                            "optional": True
                        }
                    },
                    "additionalProperties": False,
                    "required": ["title", "content"]
                },
            },
        }
