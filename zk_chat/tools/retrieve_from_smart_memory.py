import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.console_gateway import ConsoleGateway
from zk_chat.memory.smart_memory import SmartMemory
from zk_chat.tools.tool_helpers import build_descriptor

logger = structlog.get_logger()


def format_memory_results(documents: list[list[str]], distances: list[list[float]]) -> str:
    formatted_results = []
    for i, (doc, distance) in enumerate(zip(documents, distances, strict=False), 1):
        if len(distance) > 0:
            relevance = 1 - distance[0]
            formatted_results.append(f"{i}. [Relevance: {relevance:.2%}] {doc[0]}")

    if len(formatted_results) == 0:
        return "No relevant information found in memory."

    return "Found relevant information:\n" + "\n\n".join(formatted_results)


class RetrieveFromSmartMemory(LLMTool):
    def __init__(self, smart_memory: SmartMemory, console_gateway: ConsoleGateway) -> None:
        self.memory = smart_memory
        self.console_gateway = console_gateway

    def run(self, query: str) -> str:
        self.console_gateway.tool_info(f"Checking memory for anything about {query}")
        results = self.memory.retrieve(query, 10)
        information = format_memory_results(results["documents"], results["distances"])
        self.console_gateway.tool_info(information)
        return information

    @property
    def descriptor(self) -> dict:
        return build_descriptor(
            name="retrieve_from_smart_memory",
            description="Search for stored facts and context about the user that might "
            "help understand their current request better. Use this when you "
            "need to recall previously stored information about the user's preferences, "
            "environment, or circumstances to provide more personalized and contextually "
            "appropriate responses.",
            properties={
                "query": {
                    "type": "string",
                    "description": "The aspect of the user or their context you want to learn more about. "
                    "Frame your query to find relevant stored facts about the user's "
                    "preferences, environment, or circumstances.",
                },
            },
            required=["query"],
        )
