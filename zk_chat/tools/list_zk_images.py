import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.zettelkasten import Zettelkasten

logger = structlog.get_logger()


class ListZkImages(LLMTool):
    def __init__(self, zk: Zettelkasten, console_service: RichConsoleService | None = None):
        self.zk = zk
        self.console_service = console_service or RichConsoleService()

    def run(self, **kwargs) -> str:
        """
        List all image file paths in the Zettelkasten vault.

        Returns:
            A simple list of all image file paths (jpg, jpeg, png).
        """
        self.console_service.print("[tool.info]Listing all available images[/]")
        image_extensions = ['.jpg', '.jpeg', '.png']
        paths = list(self.zk.filesystem_gateway.iterate_files_by_extensions(image_extensions))
        logger.info("Listed all available images", paths=paths, count=len(paths))
        return "\n".join(paths) if paths else "No image files found in the vault."

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "list_images",
                "description": "List all image file paths in the Zettelkasten vault. Returns "
                               "paths to JPG, JPEG, and PNG files that can be analyzed or "
                               "referenced. Use this when you need to see what image files are available in the "
                               "system.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            },
        }
