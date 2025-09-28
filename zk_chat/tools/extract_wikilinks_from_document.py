import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.services.link_traversal_service import LinkTraversalService
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class ExtractWikilinksFromDocument(LLMTool):
    def __init__(self, zk: Zettelkasten, console_service: RichConsoleService | None = None):
        self.zk = zk
        self.console_service = console_service or RichConsoleService()
        # Create link traversal service using the zettelkasten's filesystem gateway
        self.link_service = LinkTraversalService(zk.filesystem_gateway)

    def run(self, relative_path: str) -> str:
        """
        Extract all wikilinks from a document with their line numbers and context.

        Args:
            relative_path: The relative path to the document to analyze

        Returns:
            JSON string containing list of WikiLinkReference objects
        """
        logger.info("Extracting wikilinks from document", relative_path=relative_path)

        if not self.zk.document_exists(relative_path):
            return f"Document not found at {relative_path}"

        # Use the link traversal service to extract wikilinks
        wikilink_references = self.link_service.extract_wikilinks_from_document(relative_path)

        console_msg = f"[tool.info]Found {len(wikilink_references)} wikilinks in {relative_path}[/]"
        self.console_service.print(console_msg)

        # Convert to JSON for return
        result = [ref.model_dump() for ref in wikilink_references]
        return str(result)

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "extract_wikilinks_from_document",
                "description": ("Extract all wikilinks from a document along with their line numbers and "
                                "context snippets. This provides fast, local analysis of a document's "
                                "explicit connections to other documents without requiring semantic "
                                "processing. Use this to quickly discover what documents are directly "
                                "referenced from a given document."),
                "parameters": {
                    "type": "object",
                    "properties": {
                        "relative_path": {
                            "type": "string",
                            "description": ("The relative path within the Zettelkasten of the document "
                                            "to analyze for wikilinks.")
                        }
                    },
                    "required": ["relative_path"]
                },
            },
        }
