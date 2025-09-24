from unittest.mock import Mock, patch

from rich.console import Console
from rich.theme import Theme

from zk_chat.console_service import RichConsoleService


class DescribeRichConsoleService:
    """Tests for the RichConsoleService component."""
    
    def should_be_instantiated_with_theme_and_console(self):
        service = RichConsoleService()
        
        assert isinstance(service, RichConsoleService)
        assert isinstance(service.theme, Theme)
        assert isinstance(service.console, Console)
    
    def should_include_chat_theme_colors(self):
        service = RichConsoleService()
        
        theme_styles = service.theme.styles
        assert "chat.user" in theme_styles
        assert "chat.assistant" in theme_styles
        assert "chat.system" in theme_styles
        assert "tool.info" in theme_styles
    
    def should_include_banner_theme_colors(self):
        service = RichConsoleService()
        
        theme_styles = service.theme.styles
        assert "banner.title" in theme_styles
        assert "banner.copyright" in theme_styles
        assert "banner.info.label" in theme_styles
        assert "banner.info.value" in theme_styles
        assert "banner.warning.unsafe" in theme_styles
        assert "banner.warning.git" in theme_styles
    
    @patch('zk_chat.console_service.Prompt')
    def should_provide_input_method_with_prompt(self, mock_prompt):
        mock_prompt.ask.return_value = "test input"
        service = RichConsoleService()
        
        result = service.input("Test prompt: ")
        
        mock_prompt.ask.assert_called_once_with("Test prompt: ", console=service.console)
        assert result == "test input"
    
    @patch('zk_chat.console_service.Prompt')
    def should_provide_input_method_without_prompt(self, mock_prompt):
        mock_prompt.ask.return_value = "test input"
        service = RichConsoleService()
        
        result = service.input()
        
        mock_prompt.ask.assert_called_once_with("", console=service.console)
        assert result == "test input"
    
    def should_provide_print_method(self):
        service = RichConsoleService()
        service.console = Mock()
        
        service.print("test message", style="bold")
        
        service.console.print.assert_called_once_with("test message", style="bold")
    
    def should_provide_access_to_console_instance(self):
        service = RichConsoleService()
        
        console = service.get_console()
        
        assert console is service.console
        assert isinstance(console, Console)