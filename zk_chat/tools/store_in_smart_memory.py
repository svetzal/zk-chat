import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.tool_helpers import build_descriptor, log_and_return_error

logger = structlog.get_logger()


class StoreInSmartMemory(LLMTool):
    """LLM tool that persists a fact or context snippet into the vector-backed smart memory."""

    def __init__(self, smart_memory: SmartMemory, console_gateway: ConsoleGateway) -> None:
        """Store the smart memory service and console gateway used during write operations."""
        self.memory = smart_memory
        self.console_gateway = console_gateway

    def run(self, information: str) -> str:
        """Store ``information`` in smart memory and return a confirmation string."""
        self.console_gateway.tool_info(f"Storing information to memory: {information}")
        try:
            self.memory.store(information)
            return "Information stored in long term memory."
        except Exception as e:  # broad catch: LLM trust boundary over opaque ChromaDB backend
            return log_and_return_error(logger, f"Error storing information in memory: {str(e)}")

    @property
    def descriptor(self) -> dict:
        """Return the OpenAI-style function descriptor for the ``store_in_smart_memory`` tool."""
        return build_descriptor(
            name="store_in_smart_memory",
            description="Store important facts and contextual information about the user "
            "and their surroundings for future reference. Use this when you "
            "learn new information about the user's preferences, environment, or circumstances "
            "that might be relevant for future interactions.",
            properties={
                "information": {
                    "type": "string",
                    "description": "The fact or contextual information to store. This should be a clear, "
                    "concise statement about the user, their preferences, environment, "
                    "or circumstances.",
                }
            },
            required=["information"],
        )
