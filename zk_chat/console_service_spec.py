from unittest.mock import Mock

from rich.console import Console
from rich.theme import Theme

from zk_chat.console_service import ConsoleGateway


class DescribeConsoleGateway:
    """Tests for the ConsoleGateway component.

    ConsoleGateway wraps Rich Console — Mock(spec=Console) is acceptable here
    because this gateway test exists specifically to verify the Rich Console
    library boundary is called correctly.
    """

    def should_be_instantiated_with_theme_and_console(self):
        service = ConsoleGateway()

        assert isinstance(service, ConsoleGateway)
        assert isinstance(service.theme, Theme)
        assert isinstance(service.console, Console)

    def should_include_chat_theme_colors(self):
        service = ConsoleGateway()

        theme_styles = service.theme.styles
        assert "chat.user" in theme_styles
        assert "chat.assistant" in theme_styles
        assert "chat.system" in theme_styles
        assert "tool.info" in theme_styles

    def should_include_banner_theme_colors(self):
        service = ConsoleGateway()

        theme_styles = service.theme.styles
        assert "banner.title" in theme_styles
        assert "banner.copyright" in theme_styles
        assert "banner.info.label" in theme_styles
        assert "banner.info.value" in theme_styles
        assert "banner.warning.unsafe" in theme_styles
        assert "banner.warning.git" in theme_styles

    def should_provide_print_method(self):
        service = ConsoleGateway()
        service.console = Mock(spec=Console)

        service.print("test message", style="bold")

        service.console.print.assert_called_once_with("test message", style="bold")

    def should_provide_access_to_console_instance(self):
        service = ConsoleGateway()

        console = service.get_console()

        assert console is service.console
        assert isinstance(console, Console)
