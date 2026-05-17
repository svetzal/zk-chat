from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from zk_chat.commands.gui import gui_app
from zk_chat.console_gateway import ConsoleGateway


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_console():
    return Mock(spec=ConsoleGateway)


@pytest.fixture
def obj(mock_console):
    return {"console_gateway": mock_console}


class DescribeLaunch:
    """Tests for the launch command."""

    def should_print_warning_when_vault_argument_provided(self, runner, mock_console, obj):
        with patch("zk_chat.qt.main"):
            runner.invoke(gui_app, ["launch", "--vault", "/some/vault"], obj=obj)

        mock_console.print.assert_any_call(
            "[yellow]Note:[/] Vault parameter (/some/vault) will be ignored."
        )

    def should_call_run_gui_when_launch_succeeds(self, runner, obj):
        with patch("zk_chat.qt.main") as mock_qt_main:
            runner.invoke(gui_app, ["launch"], obj=obj)

        mock_qt_main.assert_called_once()

    def should_exit_with_code_1_when_import_error_occurs(self, runner, obj):
        with patch.dict("sys.modules", {"zk_chat.qt": None}):
            result = runner.invoke(gui_app, ["launch"], obj=obj)

        assert result.exit_code == 1

    def should_print_dependency_instructions_on_import_error(self, runner, mock_console, obj):
        with patch.dict("sys.modules", {"zk_chat.qt": None}):
            runner.invoke(gui_app, ["launch"], obj=obj)

        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("pip install" in call for call in calls)

    def should_exit_with_code_1_on_os_error(self, runner, obj):
        with patch("zk_chat.qt.main", side_effect=OSError("display error")):
            result = runner.invoke(gui_app, ["launch"], obj=obj)

        assert result.exit_code == 1

    def should_exit_with_code_1_on_runtime_error(self, runner, obj):
        with patch("zk_chat.qt.main", side_effect=RuntimeError("gui failed")):
            result = runner.invoke(gui_app, ["launch"], obj=obj)

        assert result.exit_code == 1

    def should_print_error_message_on_os_error(self, runner, mock_console, obj):
        with patch("zk_chat.qt.main", side_effect=OSError("display error")):
            runner.invoke(gui_app, ["launch"], obj=obj)

        calls = [str(call) for call in mock_console.print.call_args_list]
        assert any("display error" in call for call in calls)


class DescribeGuiDefault:
    """Tests for the gui_default callback."""

    def should_invoke_launch_when_launch_subcommand_given(self, runner, obj):
        with patch("zk_chat.qt.main") as mock_qt_main:
            runner.invoke(gui_app, ["launch"], obj=obj)

        mock_qt_main.assert_called_once()
