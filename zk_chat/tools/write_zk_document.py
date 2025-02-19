from typing import Optional, Any

import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.models import ZkDocument
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class WriteZkDocument(LLMTool):
    def __init__(self, zk: Zettelkasten):
        self.zk = zk

    def run(self, relative_path: str, content: str, metadata: Optional[dict[str, Any]] = None) -> str:
        print("Writing document at", relative_path)
        augmented_metadata = metadata or {} | {"reviewed": False}
        logger.info("writing file", relative_path=relative_path, metadata=augmented_metadata, content=content)
        document = ZkDocument(relative_path=relative_path, metadata=augmented_metadata or {}, content=content)
        self.zk.write_zk_document(document)
        return f"Successfully wrote to {document.relative_path}"

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "write_document",
                "description": "Write document to a file in the Zettelkasten.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": "The relative path within the Zettelkasten to which the file should be written."
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
                    "required": ["relative_path", "content"]
                },
            },
        }
