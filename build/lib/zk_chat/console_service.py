from rich.console import Console
from rich.prompt import Prompt
from rich.theme import Theme


class RichConsoleService:
    """Service for consistent Rich Console usage throughout the application."""
    
    def __init__(self):
        # Define a consistent theme for the application
        self.theme = Theme({
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
        })
        
        self.console = Console(theme=self.theme)
    
    def print(self, *args, **kwargs):
        """Print using Rich Console."""
        self.console.print(*args, **kwargs)
    
    def input(self, prompt: str = "") -> str:
        """Get user input using Rich Prompt."""
        return Prompt.ask(prompt, console=self.console)
    
    def get_console(self) -> Console:
        """Get the underlying Console instance for advanced usage."""
        return self.console