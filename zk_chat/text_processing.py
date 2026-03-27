"""Pure text processing utilities."""

import re


def strip_thinking(text: str) -> str:
    """Remove <think>...</think> blocks from text.

    Some models (like Qwen) output chain-of-thought reasoning in <think> tags.
    This function strips those blocks to get the actual response content.

    Parameters
    ----------
    text : str
        The text that may contain <think> blocks

    Returns
    -------
    str
        The text with all <think>...</think> blocks removed
    """
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
