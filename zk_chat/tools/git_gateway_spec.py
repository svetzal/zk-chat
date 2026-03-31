import subprocess
from unittest.mock import MagicMock, patch

import pytest

from zk_chat.tools.git_gateway import GitGateway


@pytest.fixture
def gateway():
    return GitGateway(base_path="/fake/repo")


class DescribeGitGateway:
    def should_store_base_path_on_init(self, gateway):
        assert gateway.base_path == "/fake/repo"

    class DescribeRunGitCommand:
        def should_return_true_and_stdout_on_success(self, gateway):
            mock_result = MagicMock()
            mock_result.stdout = "output text"

            with patch("subprocess.run", return_value=mock_result) as mock_run:
                success, output = gateway._run_git_command(["git", "status"])

            assert success is True
            assert output == "output text"
            mock_run.assert_called_once_with(
                ["git", "status"],
                cwd="/fake/repo",
                capture_output=True,
                text=True,
                check=True,
            )

        def should_return_false_and_stderr_on_called_process_error(self, gateway):
            error = subprocess.CalledProcessError(1, "git", stderr="fatal: not a repository")

            with patch("subprocess.run", side_effect=error):
                success, output = gateway._run_git_command(["git", "status"])

            assert success is False
            assert output == "fatal: not a repository"

        def should_return_false_and_error_message_on_os_error(self, gateway):
            error = OSError("git not found")

            with patch("subprocess.run", side_effect=error):
                success, output = gateway._run_git_command(["git", "status"])

            assert success is False
            assert "git not found" in output

    class DescribeAddAllFiles:
        def should_run_git_add_all(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(True, "")) as mock_cmd:
                gateway.add_all_files()

            mock_cmd.assert_called_once_with(["git", "add", "--all"])

        def should_return_result_from_git_command(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(True, "staged output")):
                success, output = gateway.add_all_files()

            assert success is True
            assert output == "staged output"

    class DescribeGetStatus:
        def should_run_git_status_porcelain(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(True, "M file.py")) as mock_cmd:
                gateway.get_status()

            mock_cmd.assert_called_once_with(["git", "status", "--porcelain"])

        def should_return_result_from_git_command(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(True, "M file.py")):
                success, output = gateway.get_status()

            assert success is True
            assert output == "M file.py"

    class DescribeGetDiff:
        def should_run_git_diff_head(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(True, "diff output")) as mock_cmd:
                gateway.get_diff()

            mock_cmd.assert_called_once_with(["git", "diff", "HEAD"])

        def should_return_result_from_git_command(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(True, "diff output")):
                success, output = gateway.get_diff()

            assert success is True
            assert output == "diff output"

    class DescribeCommit:
        def should_run_git_commit_with_message(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(True, "")) as mock_cmd:
                gateway.commit("Fix the bug")

            mock_cmd.assert_called_once_with(["git", "commit", "-m", "Fix the bug"])

        def should_return_result_from_git_command(self, gateway):
            with patch.object(gateway, "_run_git_command", return_value=(False, "nothing to commit")):
                success, output = gateway.commit("empty")

            assert success is False
            assert output == "nothing to commit"

    class DescribeSetup:
        def should_create_gitignore_when_absent(self, tmp_path):
            gateway = GitGateway(base_path=str(tmp_path))

            with patch.object(gateway, "_run_git_command", return_value=(True, "")):
                gateway.setup()

            gitignore = tmp_path / ".gitignore"
            assert gitignore.exists()
            content = gitignore.read_text()
            assert ".zk_chat*" in content
            assert ".obsidian" in content
            assert ".vscode" in content

        def should_not_overwrite_existing_gitignore(self, tmp_path):
            gateway = GitGateway(base_path=str(tmp_path))
            gitignore = tmp_path / ".gitignore"
            gitignore.write_text("custom content\n")

            with patch.object(gateway, "_run_git_command", return_value=(True, "")):
                gateway.setup()

            assert gitignore.read_text() == "custom content\n"

        def should_initialize_git_repo_when_dot_git_absent(self, tmp_path):
            gateway = GitGateway(base_path=str(tmp_path))

            with patch.object(gateway, "_run_git_command", return_value=(True, "")) as mock_cmd:
                gateway.setup()

            commands_called = [call.args[0] for call in mock_cmd.call_args_list]
            assert ["git", "init"] in commands_called
            assert ["git", "add", "--all"] in commands_called
            assert ["git", "commit", "-m", "Initial commit"] in commands_called

        def should_not_initialize_git_repo_when_dot_git_exists(self, tmp_path):
            gateway = GitGateway(base_path=str(tmp_path))
            (tmp_path / ".git").mkdir()

            with patch.object(gateway, "_run_git_command", return_value=(True, "")) as mock_cmd:
                gateway.setup()

            commands_called = [call.args[0] for call in mock_cmd.call_args_list]
            assert ["git", "init"] not in commands_called
