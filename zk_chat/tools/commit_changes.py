import structlog
from mojentic.llm import LLMBroker
from mojentic.llm.gateways.models import LLMMessage
from mojentic.llm.tools.llm_tool import LLMTool
from pydantic import BaseModel, Field

from zk_chat.tools.git_gateway import GitGateway

logger = structlog.get_logger()


class CommitChanges(LLMTool):

    base_path: str
    llm: LLMBroker
    git: GitGateway

    def __init__(self, base_path: str, llm: LLMBroker, git: GitGateway):
        self.base_path = base_path
        self.llm = llm
        self.git = git

    def run(self) -> str:
        print("Committing changes in vault folder")

        try:
            # Add all files to git staging
            success, message = self.git.add_all_files()
            if not success:
                return f"Error adding files: {message}"

            # Check if there are any changes to commit
            success, status_output = self.git.get_status()
            if not success:
                return f"Error checking status: {status_output}"

            if not status_output.strip():
                return "No changes to commit in the vault folder."

            # Get the diff to summarize changes
            success, diff_output = self.git.get_diff()
            if not success:
                return f"Error getting diff: {diff_output}"

            commit_message = self._generate_commit_message(diff_output)

            # Commit the changes
            success, commit_output = self.git.commit(commit_message)
            if not success:
                return f"Error committing changes: {commit_output}"

            return f"Successfully committed changes: '{commit_message}'"
        except Exception as e:
            logger.error("Unexpected error", error=str(e))
            return f"Unexpected error committing changes: {str(e)}"

    def _generate_commit_message(self, diff_summary: str) -> str:
        """
        Generate a one-line commit message based on the diff summary.

        Parameters
        ----------
        diff_summary : str
            The output of git diff --staged --stat

        Returns
        -------
        str
            A one-line commit message summarizing the changes
        """

        class GitCommitMessage(BaseModel):
            message: str = Field(..., description="A brief description of changes suitable for a git commit")

        return self.llm.generate_object([
            LLMMessage(content=f"""
Summarize the provided git diff output in a one-line commit message. Ignore any changes to the front-matter.

```
{diff_summary}
```
""".strip())
        ],
        object_model=GitCommitMessage).message

    @property
    def descriptor(self) -> dict:
        return {
            "type": "function",
            "function": {
                "name": "commit_changes",
                "description": "Save all changes made to the Zettelkasten knowledge base by creating a Git commit. Use this after making modifications to documents (creating, updating, or renaming) to permanently store those changes in the version control system. This ensures your changes are preserved and can be tracked over time.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                },
            },
        }
