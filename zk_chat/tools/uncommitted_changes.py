from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.tool_helpers import PASSTHROUGH, GitToolError, build_descriptor, checked, tool_boundary


class UncommittedChanges(LLMTool):
    """LLM tool that shows all staged-but-uncommitted changes in the vault as a git diff."""

    def __init__(self, base_path: str, git: GitGateway, console_gateway: ConsoleGateway) -> None:
        """Store the vault path, git gateway, and console gateway used to inspect changes."""
        self.base_path = base_path
        self.git = git
        self.console_gateway = console_gateway

    @tool_boundary({GitToolError: PASSTHROUGH, OSError: "Unexpected error getting uncommitted changes"})
    def run(self) -> str:
        """Stage all files and return the current git diff, or a no-changes message."""
        self.console_gateway.tool_info("Getting uncommitted changes in vault folder")
        checked(self.git.add_all_files(), "Error adding files")
        diff_output = checked(self.git.get_diff(), "Error getting diff")

        if not diff_output.strip():
            return "No uncommitted changes in the vault folder."

        return f"Uncommitted changes in the vault folder:\n{diff_output}"

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``get_uncommitted_changes`` tool."""
        return build_descriptor(
            name="get_uncommitted_changes",
            description="View all changes made to the Zettelkasten knowledge base that "
            "haven't been committed yet. Use this to review your modifications "
            "before committing them permanently with the commit_changes tool. "
            "This helps you verify what documents have been created, modified, "
            "or deleted since the last commit.",
        )
