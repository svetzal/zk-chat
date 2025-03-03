import structlog
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.memory.smart_memory import SmartMemory

logger = structlog.get_logger()


class StoreInSmartMemory(LLMTool):
    def __init__(self, smart_memory: SmartMemory):
        self.memory = smart_memory

    def run(self, information: str) -> str:
        print("Storing information to memory", information)
        self.memory.store(information)
        return "Information stored in long term memory."

    @property
    def descriptor(self):
        return {
            "type": "function",
            "function": {
                "name": "store_in_smart_memory",
                "description": "Store important facts and contextual information about the user and their surroundings for future reference. Use this when you learn new information about the user's preferences, environment, or circumstances that might be relevant for future interactions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "information": {
                            "type": "string",
                            "description": "The fact or contextual information to store. This should be a clear, concise statement about the user, their preferences, environment, or circumstances."
                        }
                    },
                    "required": ["information"]
                },
            },
        }
