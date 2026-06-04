import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.tool_helpers import GitToolError, build_descriptor, checked

logger = structlog.get_logger()


class UncommittedChanges(LLMTool):
    def __init__(self, base_path: str, git: GitGateway, console_gateway: ConsoleGateway) -> None:
        self.base_path = base_path
        self.git = git
        self.console_gateway = console_gateway

    def run(self) -> str:
        self.console_gateway.tool_info("Getting uncommitted changes in vault folder")

        try:
            checked(self.git.add_all_files(), "Error adding files")
            diff_output = checked(self.git.get_diff(), "Error getting diff")

            if not diff_output.strip():
                return "No uncommitted changes in the vault folder."

            return f"Uncommitted changes in the vault folder:\n{diff_output}"
        except GitToolError as e:
            return str(e)
        except OSError as e:
            logger.error("Unexpected error", error=str(e))
            return f"Unexpected error getting uncommitted changes: {str(e)}"

    @property
    def descriptor(self) -> dict:
        return build_descriptor(
            name="get_uncommitted_changes",
            description="View all changes made to the Zettelkasten knowledge base that "
            "haven't been committed yet. Use this to review your modifications "
            "before committing them permanently with the commit_changes tool. "
            "This helps you verify what documents have been created, modified, "
            "or deleted since the last commit.",
        )
