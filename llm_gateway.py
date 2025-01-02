from ollama import ChatResponse, chat, Options


class LLMGateway():
    def __init__(self, model):
        self.model = model

    def generate_text(self, messages, temperature=1.0, num_ctx=32768, num_predict=8192):
        response: ChatResponse = chat(
            model=self.model,
            messages=messages,
            options=Options(temperature=temperature, num_ctx=num_ctx, num_predict=num_predict),
        )
        return response.message.content
