from rich.console import Console
from rich.prompt import Prompt
from rich.theme import Theme


class ConsoleGateway:
    """Service for consistent Rich Console usage throughout the application."""

    def __init__(self) -> None:
        """Initialize the Rich console with an application-wide theme."""
        self.theme = Theme(
            {
                "banner.title": "bold bright_cyan",
                "banner.copyright": "bright_blue",
                "banner.info.label": "white",
                "banner.info.value": "green",
                "banner.warning.unsafe": "bold bright_red",
                "banner.warning.git": "yellow",
                "chat.user": "bold blue",
                "chat.assistant": "green",
                "chat.system": "dim yellow",
                "tool.info": "dim cyan",
            }
        )

        self.console = Console(theme=self.theme)

    def print(self, *args, **kwargs) -> None:
        """Print to the themed Rich console, forwarding all args and kwargs."""
        self.console.print(*args, **kwargs)

    def input(self, prompt: str = "") -> str:
        """Prompt the user for input using the themed Rich console."""
        return Prompt.ask(prompt, console=self.console)

    def tool_info(self, message: str) -> None:
        """Print a tool-activity message styled with the ``tool.info`` theme token."""
        self.console.print(f"[tool.info]{message}[/]")

    def get_console(self) -> Console:
        """Return the underlying Rich ``Console`` instance for direct access."""
        return self.console

