import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.memory.smart_memory import SmartMemory

logger = structlog.get_logger()


class RetrieveFromSmartMemory(LLMTool):
    def __init__(self, smart_memory: SmartMemory):
        self.memory = smart_memory

    def run(self, query: str) -> str:
        print("Checking memory for anything about", query)
        results = self.memory.retrieve(query, 10)

        formatted_results = []
        for i, (doc, distance) in enumerate(zip(results['documents'], results['distances']), 1):
            if len(distance) > 0:
                relevance = 1 - distance[0]  # Convert distance to similarity score (0-1)
                formatted_results.append(f"{i}. [Relevance: {relevance:.2%}] {doc[0]}")

        if len(formatted_results) == 0:
            message = "No relevant information found in memory."
            print(message)
            return message

        information = "Found relevant information:\n" + "\n\n".join(formatted_results)
        print(information)
        return information

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "retrieve_from_smart_memory",
                "description": "Search for stored facts and context about the user that might help understand their current request better. Use this when you need to recall previously stored information about the user's preferences, environment, or circumstances to provide more personalized and contextually appropriate responses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The aspect of the user or their context you want to learn more about. Frame your query to find relevant stored facts about the user's preferences, environment, or circumstances."
                        },
                    },
                    "required": ["query"]
                },
            },
        }
