import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class FindBacklinks(LLMTool):
    def __init__(self, zk: Zettelkasten, console_service: RichConsoleService | None = None):
        self.zk = zk
        self.console_service = console_service or RichConsoleService()
        # Create link traversal service using the zettelkasten's filesystem gateway
        self.link_service = LinkTraversalService(zk.filesystem_gateway)

    def run(self, target_document: str) -> str:
        """
        Find all documents that contain wikilinks pointing to the target document.

        Args:
            target_document: The document to find backlinks to (can be relative path or wikilink text)

        Returns:
            JSON string containing list of BacklinkResult objects
        """
        logger.info("Finding backlinks to document", target_document=target_document)

        # Use the link traversal service to find backlinks
        backlink_results = self.link_service.find_backlinks(target_document)

        console_msg = f"[tool.info]Found {len(backlink_results)} backlinks to {target_document}[/]"
        self.console_service.print(console_msg)

        # Convert to JSON for return
        result = [backlink.model_dump() for backlink in backlink_results]
        return str(result)

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "find_backlinks",
                "description": ("Find all documents that contain wikilinks pointing to a specific target "
                                "document. This provides fast discovery of what documents reference a "
                                "given document, enabling reverse navigation through the knowledge graph. "
                                "Returns documents with context snippets showing how they reference the "
                                "target document. Use this to understand what content builds upon or "
                                "references a particular document."),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_document": {
                            "type": "string",
                            "description": ("The target document to find backlinks to. Can be either a "
                                            "relative path (e.g., 'concepts/systems-thinking.md') or "
                                            "wikilink text (e.g., 'Systems Thinking'). The service will "
                                            "handle resolution and find all documents that link to this target.")
                        }
                    },
                    "required": ["target_document"]
                },
            },
        }