"""Pure text processing utilities."""

import re


def strip_thinking(text: str) -> str:
    """Strips <think>...</think> blocks used by Qwen-style chain-of-thought models."""
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
