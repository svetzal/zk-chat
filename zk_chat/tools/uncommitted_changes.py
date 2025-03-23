import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.tools.git_gateway import GitGateway

logger = structlog.get_logger()


class UncommittedChanges(LLMTool):
    def __init__(self, base_path: str, git: GitGateway):
        self.base_path = base_path
        self.git = git

    def run(self) -> str:
        print("Getting uncommitted changes in vault folder")

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
                "description": "Get a summary of uncommitted changes that are pending in the vault.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            },
        }
