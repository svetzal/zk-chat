import os
import subprocess
from typing import Tuple

import structlog

logger = structlog.get_logger()


class GitGateway:
    """
    Gateway class for Git operations.
    Provides an interface for executing git commands and handling errors.
    """
    def __init__(self, base_path: str):
        """
        Initialize the GitGateway with the repository path.
        
        Parameters
        ----------
        base_path : str
            The path to the git repository
        """
        self.base_path = base_path

    def _run_git_command(self, command: list) -> Tuple[bool, str]:
        """
        Run a git command and handle errors.
        
        Parameters
        ----------
        command : list
            The git command to run as a list of strings
            
        Returns
        -------
        Tuple[bool, str]
            A tuple containing a success flag and the command output or error message
        """
        try:
            result = subprocess.run(
                command,
                cwd=self.base_path,
                capture_output=True,
                text=True,
                check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Error executing git command: {command[0]}", error=str(e), stderr=e.stderr)
            return False, e.stderr
        except Exception as e:
            logger.error(f"Unexpected error in git command: {command[0]}", error=str(e))
            return False, str(e)

    def add_all_files(self) -> Tuple[bool, str]:
        """
        Add all files to git staging.
        
        Returns
        -------
        Tuple[bool, str]
            A tuple containing a success flag and the command output or error message
        """
        return self._run_git_command(["git", "add", "--all"])

    def get_status(self) -> Tuple[bool, str]:
        """
        Get the git status in porcelain format.
        
        Returns
        -------
        Tuple[bool, str]
            A tuple containing a success flag and the status output or error message
        """
        return self._run_git_command(["git", "status", "--porcelain"])

    def get_diff(self) -> Tuple[bool, str]:
        """
        Get the git diff against HEAD.
        
        Returns
        -------
        Tuple[bool, str]
            A tuple containing a success flag and the diff output or error message
        """
        return self._run_git_command(["git", "diff", "HEAD"])

    def commit(self, message: str) -> Tuple[bool, str]:
        """
        Commit changes with the provided message.
        
        Parameters
        ----------
        message : str
            The commit message
            
        Returns
        -------
        Tuple[bool, str]
            A tuple containing a success flag and the commit output or error message
        """
        return self._run_git_command(["git", "commit", "-m", message])

    def setup(self):
        # Create a .gitignore file if it does not exist
        gitignore_path = os.path.join(self.base_path, ".gitignore")
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, "w") as f:
                f.write(".zk_chat*\n.obsidian\n.vscode\n")

        # Initialize the git repository if it does not exist
        if not os.path.exists(os.path.join(self.base_path, ".git")):
            self._run_git_command(["git", "init"])
            self._run_git_command(["git", "add", "--all"])
            self._run_git_command(["git", "commit", "-m", "Initial commit"])