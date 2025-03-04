from typing import Optional, Any

import structlog
import yaml
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.models import ZkDocument
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class CreateOrOverwriteZkDocument(LLMTool):
    def __init__(self, zk: Zettelkasten):
        self.zk = zk

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
        relative_path = f"{self._sanitize_filename(title)}.md"
        print("Writing document at", relative_path)
        try:
            augmented_metadata = metadata or {} | {"reviewed": False}
            logger.info("writing file", relative_path=relative_path, metadata=augmented_metadata, content=content)
            document = ZkDocument(relative_path=relative_path, metadata=augmented_metadata or {}, content=content)
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
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "create_or_overwrite_document",
                "description": "Write document to a file in the Zettelkasten, overwriting the content if it already exists. Returns a success message if the write operation succeeds, or a detailed error message if it fails (e.g., due to filesystem permissions, disk space issues, or invalid metadata).",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "The title of the document."
                        },
                        "content": {
                            "type": "string",
                            "description": "The content to write to the file."
                        },
                        "metadata": {
                            "type": "object",
                            "description": "The metadata to write to the file in JSON format.",
                            "optional": True
                        }
                    },
                    "additionalProperties": False,
                    "required": ["title", "content"]
                },
            },
        }
