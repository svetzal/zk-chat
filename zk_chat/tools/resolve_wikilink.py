import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.tools.tool_helpers import build_descriptor

logger = structlog.get_logger()


class ResolveWikiLink(LLMTool):
    """LLM tool that resolves a wikilink string to its corresponding vault relative path."""

    fs: MarkdownFilesystemGateway

    def __init__(self, fs: MarkdownFilesystemGateway) -> None:
        """Store the filesystem gateway used to walk the vault and match wikilink titles."""
        self.fs = fs

    def run(self, wikilink: str) -> str:
        """Resolve ``wikilink`` to a relative path, or return an error if unresolvable."""
        logger.info("Resolving wikilink", wikilink=wikilink)

        try:
            relative_path = self.fs.resolve_wikilink(wikilink)
            return "relative_path: " + relative_path
        except ValueError:  # intentional domain control flow: no match is a valid result, not a backend failure
            return "There is no document currently present matching the wikilink provided."

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``resolve_wikilink`` tool."""
        return build_descriptor(
            name="resolve_wikilink",
            description="Determine if a wikilink is valid (eg [[link title]]), and if so "
            "return the relative_path of the target document or file. Returns "
            "an error if there is no document present matching the wikilink.",
            properties={
                "wikilink": {
                    "type": "string",
                    "description": "The wikilink you need to resolve to a relative_path, wrapped in "
                    "double-square-brackets, in the form of [[Document Title]] or [[@Person "
                    "Name]].",
                }
            },
            required=["wikilink"],
        )
