import structlog
from mojentic.llm import LLMBroker, MessageBuilder
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway

logger = structlog.get_logger()


class AnalyzeImage(LLMTool):
    def __init__(self, fs: MarkdownFilesystemGateway, llm: LLMBroker,
                 console_service: RichConsoleService | None = None):
        self.fs = fs
        self.llm = llm
        self.console_service = console_service or RichConsoleService()

    def run(self, relative_path: str) -> str:
        logger.info("Analyzing image", relative_path=relative_path)
        if not self.fs.path_exists(relative_path):
            return f"Image not found at {relative_path}"

        message = MessageBuilder("Describe what you see in the image in plain text.") \
            .add_image(self.fs.get_absolute_path_for_tool_access(relative_path)) \
            .build()
        analysis = self.llm.generate([message])

        return analysis

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "analyze_image",
                "description": "Analyze the contents of an image, returning a full description of "
                "what is visually contained within.",
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
