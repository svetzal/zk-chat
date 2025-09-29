import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class FindForwardLinks(LLMTool):
    def __init__(self, zk: Zettelkasten, console_service: RichConsoleService | None = None):
        self.zk = zk
        self.console_service = console_service or RichConsoleService()
        # Create link traversal service using the zettelkasten's filesystem gateway
        self.link_service = LinkTraversalService(zk.filesystem_gateway)

    def run(self, source_document: str) -> str:
        """
        Find all documents that are linked from the source document via wikilinks.

        Args:
            source_document: The source document to find forward links from (relative path)

        Returns:
            JSON string containing list of ForwardLinkResult objects
        """
        logger.info("Finding forward links from document", source_document=source_document)

        if not self.zk.document_exists(source_document):
            return f"Document not found at {source_document}"

        # Use the link traversal service to find forward links
        forward_link_results = self.link_service.find_forward_links(source_document)

        console_msg = f"[tool.info]Found {len(forward_link_results)} forward links from {source_document}[/]"
        self.console_service.print(console_msg)

        # Convert to JSON for return
        result = [forward_link.model_dump() for forward_link in forward_link_results]
        return str(result)

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "find_forward_links",
                "description": ("Find all documents that are linked from a specific source document "
                                "via wikilinks. This provides fast discovery of what documents a "
                                "given document references, enabling forward navigation through the "
                                "knowledge graph. Returns target documents with context snippets "
                                "showing how they are referenced from the source document. Use this "
                                "to understand what content a particular document builds upon or "
                                "references."),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "source_document": {
                            "type": "string",
                            "description": ("The relative path of the source document to find forward "
                                            "links from (e.g., 'concepts/systems-thinking.md'). The "
                                            "service will extract all wikilinks from this document and "
                                            "resolve them to their target documents.")
                        }
                    },
                    "required": ["source_document"]
                },
            },
        }