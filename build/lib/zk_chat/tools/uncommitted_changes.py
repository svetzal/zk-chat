import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_service import RichConsoleService
from zk_chat.tools.git_gateway import GitGateway

logger = structlog.get_logger()


class UncommittedChanges(LLMTool):
    def __init__(self, base_path: str, git: GitGateway, console_service: RichConsoleService = None):
        self.base_path = base_path
        self.git = git
        self.console_service = console_service or RichConsoleService()

    def run(self) -> str:
        self.console_service.print("[tool.info]Getting uncommitted changes in vault folder[/]")

        try:
            # Add all files to git staging to include new files in the diff
            success, message = self.git.add_all_files()
            if not success:
                return f"Error adding files: {message}"

            # Execute git diff command to get uncommitted changes
            # We use git diff HEAD to show all changes (both staged and unstaged)
            success, diff_output = self.git.get_diff()
            if not success:
                return f"Error getting diff: {diff_output}"

            # If there are no changes, git diff returns an empty string
            if not diff_output.strip():
                return "No uncommitted changes in the vault folder."

            return f"Uncommitted changes in the vault folder:\n{diff_output}"
        except Exception as e:
            logger.error("Unexpected error", error=str(e))
            return f"Unexpected error getting uncommitted changes: {str(e)}"

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "get_uncommitted_changes",
                "description": "View all changes made to the Zettelkasten knowledge base that haven't been committed yet. Use this to review your modifications before committing them permanently with the commit_changes tool. This helps you verify what documents have been created, modified, or deleted since the last commit.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            },
        }
