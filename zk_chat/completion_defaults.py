"""Completion settings shared by every LLM request zk-chat makes.

mojentic 3.0 leaves temperature, context window and output limit unset unless
the caller supplies them. zk-chat pins the values it has always relied on so
Ollama keeps a context window large enough for retrieved notes and tool output.
"""

from mojentic.llm import CompletionConfig

ZK_CHAT_COMPLETION_CONFIG = CompletionConfig(temperature=1.0, num_ctx=32768, max_tokens=16384)
