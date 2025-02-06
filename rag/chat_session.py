from typing import List

from mojentic.llm import LLMBroker
from mojentic.llm.gateways.models import LLMMessage, MessageRole
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway


class SizedLLMMessage(LLMMessage):
    token_length: int


class ChatSession:
    messages: List[SizedLLMMessage] = []

    def __init__(self,
                 llm: LLMBroker,
                 system_prompt: str = "You are a helpful assistant.",
                 max_context: int = 32768,
                 tokenizer_gateway: TokenizerGateway = None,
                 temperature: float = 1.0):

        self.llm = llm
        self.system_prompt = system_prompt
        self.max_context = max_context
        self.temperature = temperature

        if tokenizer_gateway is None:
            self.tokenizer_gateway = TokenizerGateway()
        else:
            self.tokenizer_gateway = tokenizer_gateway

        self.insert_message(LLMMessage(role=MessageRole.System, content=self.system_prompt))

    def send(self, query):
        self.insert_message(LLMMessage(role=MessageRole.User, content=query))
        response = self.llm.generate(self.messages, temperature=0.1)
        self.insert_message(LLMMessage(role=MessageRole.Assistant, content=response))
        return response

    def insert_message(self, message: LLMMessage):
        self.messages.append(self._build_sized_message(message))
        total_length = sum([msg.token_length for msg in self.messages])
        while total_length > self.max_context:
            total_length -= self.messages.pop(1).token_length

    def _build_sized_message(self, message):
        new_message_length = len(self.tokenizer_gateway.encode(message.content))
        new_message = SizedLLMMessage(**message.model_dump(), token_length=new_message_length)
        return new_message
