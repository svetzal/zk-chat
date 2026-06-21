import structlog
from mojentic.llm import LLMBroker, MessageBuilder
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.tools.tool_helpers import build_descriptor, log_and_return_error

logger = structlog.get_logger()


class AnalyzeImage(LLMTool):
    """LLM tool that submits a vault image to the visual LLM and returns a plain-text description."""

    def __init__(self, fs: MarkdownFilesystemGateway, llm: LLMBroker, _message_builder_factory=None) -> None:
        """Store the filesystem gateway, LLM broker, and optional message-builder factory."""
        self.fs = fs
        self.llm = llm
        self._message_builder_factory = _message_builder_factory or MessageBuilder

    def run(self, relative_path: str) -> str:
        """Analyze the image at ``relative_path`` and return a plain-text description from the LLM."""
        logger.info("Analyzing image", relative_path=relative_path)
        if not self.fs.path_exists(relative_path):
            return f"Image not found at {relative_path}"

        try:
            message = (
                self._message_builder_factory("Describe what you see in the image in plain text.")
                .add_image(self.fs.get_absolute_path_for_tool_access(relative_path))
                .build()
            )
            analysis = self.llm.generate([message])
            return analysis
        except (OSError, ConnectionError) as e:
            return log_and_return_error(logger, f"Error analyzing image at {relative_path}: {str(e)}")

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``analyze_image`` tool."""
        return build_descriptor(
            name="analyze_image",
            description="Analyze the contents of an image, returning a full description of "
            "what is visually contained within.",
            properties={
                "relative_path": {
                    "type": "string",
                    "description": "Relative path of the image to analyze",
                }
            },
            required=["relative_path"],
        )
