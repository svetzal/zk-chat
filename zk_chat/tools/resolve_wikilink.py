import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway

logger = structlog.get_logger()

class ResolveWikiLink(LLMTool):
    fs: MarkdownFilesystemGateway

    def __init__(self, fs: MarkdownFilesystemGateway):
        self.fs = fs

    def run(self, wikilink: str):
        logger.info("Resolving wikilink", wikilink=wikilink)

        try:
            relative_path = self.fs.resolve_wikilink(wikilink)
            return "relative_path: " + relative_path
        except ValueError as e:
            return "There is no document currently present matching the wikilink provided."

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "resolve_wikilink",
                "description": "Determine if a wikilink is valid, and if so return the relative_path of the target document or file. Returns an error if there is no document present matching the wikilink.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "wikilink": {
                            "type": "string",
                            "description": "The wikilink you need to resolve to a relative_path, in the form of [[Document Title]] or [[@Person Name]].",
                        }
                    },
                    "required": ["wikilink"]
                }
            }
        }