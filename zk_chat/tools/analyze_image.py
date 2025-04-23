import structlog
from mojentic.llm import LLMBroker, MessageBuilder
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class AnalyzeImage(LLMTool):
    zk: Zettelkasten
    llm: LLMBroker

    def __init__(self, zk: Zettelkasten, llm: LLMBroker):
        self.zk = zk
        self.llm = llm

    def run(self, relative_path: str) -> str:
        logger.info("Analyzing image", relative_path=relative_path)
        if not self.zk.file_exists(relative_path):
            return f"Image not found at {relative_path}"

        message = MessageBuilder("Describe what you see in the image in plain text.") \
            .add_image(self.zk.filesystem_gateway.get_full_path(relative_path)) \
            .build()
        analysis = self.llm.generate([message])

        return analysis

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "analyze_image",
                "description": "Analyze the contents of an image, returning a full description of what is visually contained within.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": "Relative path of the image to analyze",
                        }
                    },
                    "required": ["relative_path"]
                }
            }
        }
