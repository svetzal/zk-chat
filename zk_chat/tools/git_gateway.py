import os
import subprocess

import structlog

logger = structlog.get_logger()


class GitGateway:
    """
    Gateway class for Git operations.
    Provides an interface for executing git commands and handling errors.
    """

    def __init__(self, base_path: str) -> None:
        self.base_path = base_path

    def _run_git_command(self, command: list) -> tuple[bool, str]:
        try:
            result = subprocess.run(command, cwd=self.base_path, capture_output=True, text=True, check=True)
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing git command: {command[0]}", error=str(e), stderr=e.stderr)
            return False, e.stderr
        except OSError as e:
            logger.error(f"Unexpected error in git command: {command[0]}", error=str(e))
            return False, str(e)

    def add_all_files(self) -> tuple[bool, str]:
        """Stage all changes in the working tree (``git add --all``)."""
        return self._run_git_command(["git", "add", "--all"])

    def get_status(self) -> tuple[bool, str]:
        """Return the porcelain status output listing modified and untracked files."""
        return self._run_git_command(["git", "status", "--porcelain"])

    def get_diff(self) -> tuple[bool, str]:
        """Return the unified diff of all changes since the last commit."""
        return self._run_git_command(["git", "diff", "HEAD"])

    def commit(self, message: str) -> tuple[bool, str]:
        """Create a commit with the given message; returns ``(False, stderr)`` on failure."""
        return self._run_git_command(["git", "commit", "-m", message])

    def setup(self) -> None:
        """Initialise a git repository in the vault if one does not already exist."""
        gitignore_path = os.path.join(self.base_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w") as f:
                f.write(".zk_chat*\n.obsidian\n.vscode\n")

        if not os.path.exists(os.path.join(self.base_path, ".git")):
            self._run_git_command(["git", "init"])
            self._run_git_command(["git", "add", "--all"])
            self._run_git_command(["git", "commit", "-m", "Initial commit"])
