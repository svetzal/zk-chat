from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from zk_chat.config import Config
from zk_chat.main import app


@pytest.fixture
def runner():
    return CliRunner()


class DescribeMain:
    """Tests for the main CLI app wiring and callback."""

    def should_show_version_info_when_version_flag_given(self, runner):
        result = runner.invoke(app, ["--version", "interactive"])

        assert result.exit_code == 0
        assert "zk-chat" in result.output

    def should_include_version_number_in_output(self, runner):
        result = runner.invoke(app, ["--version", "interactive"])

        assert "Version Information" in result.output

    def should_register_gui_subcommand(self, runner):
        result = runner.invoke(app, ["--help"])

        assert "gui" in result.output

    def should_register_index_subcommand(self, runner):
        result = runner.invoke(app, ["--help"])

        assert "index" in result.output

    def should_register_mcp_subcommand(self, runner):
        result = runner.invoke(app, ["--help"])

        assert "mcp" in result.output

    def should_register_diagnose_subcommand(self, runner):
        result = runner.invoke(app, ["--help"])

        assert "diagnose" in result.output

    def should_register_bookmarks_subcommand(self, runner):
        result = runner.invoke(app, ["--help"])

        assert "bookmarks" in result.output


class DescribeInteractiveCommand:
    """Tests for the interactive command's argument handling."""

    def should_construct_init_options_with_vault_argument(self, runner):
        captured_options = []

        def mock_common_init(options, global_config_gateway, config_gateway, console_gateway):
            captured_options.append(options)
            return None

        runner.invoke(app, ["interactive", "--vault", "/some/vault"], obj={"common_init": mock_common_init})

        assert len(captured_options) == 1
        assert captured_options[0].vault == "/some/vault"

    def should_construct_init_options_with_unsafe_flag(self, runner):
        captured_options = []

        def mock_common_init(options, global_config_gateway, config_gateway, console_gateway):
            captured_options.append(options)
            return None

        runner.invoke(app, ["interactive", "--unsafe"], obj={"common_init": mock_common_init})

        assert len(captured_options) == 1
        assert captured_options[0].unsafe is True

    def should_construct_init_options_with_git_flag(self, runner):
        captured_options = []

        def mock_common_init(options, global_config_gateway, config_gateway, console_gateway):
            captured_options.append(options)
            return None

        runner.invoke(app, ["interactive", "--git"], obj={"common_init": mock_common_init})

        assert len(captured_options) == 1
        assert captured_options[0].git is True

    def should_construct_init_options_with_no_index_flag(self, runner):
        captured_options = []

        def mock_common_init(options, global_config_gateway, config_gateway, console_gateway):
            captured_options.append(options)
            return None

        runner.invoke(app, ["interactive", "--no-index"], obj={"common_init": mock_common_init})

        assert len(captured_options) == 1
        assert captured_options[0].reindex is False

    def should_invoke_run_agent_when_config_is_returned(self, runner):
        mock_config = Config(vault="/test/vault", model="llama2")
        mock_run_agent = Mock()  # Intentionally unspec'd: bare callable, not a class instance
        mock_display_banner = Mock()  # Intentionally unspec'd: bare callable, not a class instance

        runner.invoke(
            app,
            ["interactive"],
            obj={
                "common_init": lambda *args, **kwargs: mock_config,
                "run_agent": mock_run_agent,
                "display_banner": mock_display_banner,
            },
        )

        assert mock_run_agent.called
        assert mock_run_agent.call_args.args[0] is mock_config

    def should_not_invoke_run_agent_when_config_is_none(self, runner):
        mock_run_agent = Mock()  # Intentionally unspec'd: bare callable, not a class instance

        runner.invoke(
            app,
            ["interactive"],
            obj={
                "common_init": lambda *args, **kwargs: None,
                "run_agent": mock_run_agent,
            },
        )

        mock_run_agent.assert_not_called()


class DescribeQueryCommand:
    """Tests for the query command's behavior."""

    def should_exit_with_code_1_when_no_prompt_and_stdin_is_tty(self, runner):
        with patch("zk_chat.main.sys") as mock_sys:
            mock_sys.stdin.isatty.return_value = True
            result = runner.invoke(app, ["query"])

        assert result.exit_code == 1
