from mojentic.llm import LLMBroker
from mojentic.llm.gateways.models import LLMMessage
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.text_processing import strip_thinking
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.tool_helpers import PASSTHROUGH, GitToolError, build_descriptor, checked, tool_boundary


class CommitChanges(LLMTool):
    """LLM tool that stages all vault changes, generates a commit message via LLM, and commits."""

    base_path: str
    llm: LLMBroker
    git: GitGateway

    def __init__(self, base_path: str, llm: LLMBroker, git: GitGateway, console_gateway: ConsoleGateway) -> None:
        """Store the vault path, LLM broker, git gateway, and console gateway for commit operations."""
        self.base_path = base_path
        self.llm = llm
        self.git = git
        self.console_gateway = console_gateway

    @tool_boundary(
        {
            GitToolError: PASSTHROUGH,
            OSError: "Unexpected error committing changes",
            ConnectionError: "Unexpected error committing changes",
        }
    )
    def run(self) -> str:
        """Stage all changes, generate an LLM commit message, commit, and return a status string."""
        self.console_gateway.tool_info("Committing changes in vault folder")
        checked(self.git.add_all_files(), "Error adding files")
        status_output = checked(self.git.get_status(), "Error checking status")

        if not status_output.strip():
            return "No changes to commit in the vault folder."

        diff_output = checked(self.git.get_diff(), "Error getting diff")
        commit_message = self._generate_commit_message(diff_output)
        checked(self.git.commit(commit_message), "Error committing changes")

        return f"Successfully committed changes: '{commit_message}'"

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

        message = self.llm.generate(
            [
                LLMMessage(
                    content=f"""
The user is committing changes to a content repository managed by git. The following is the
output from git diff. Summarize a suitable git commit message about the content changes.
Output only the commit message, no other text, do not put it in code fences.

```
{diff_summary}
```
""".strip()
                )
            ]
        )
        return strip_thinking(message)

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``commit_changes`` tool."""
        return build_descriptor(
            name="commit_changes",
            description="Save all changes made to the Zettelkasten knowledge base by "
            "creating a Git commit. Use this after making modifications to documents (creating, "
            "updating, or renaming) to permanently store those changes in the version control "
            "system. This ensures your changes are preserved and can be tracked over time.",
        )
