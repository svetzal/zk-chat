"""Pure filename utilities for sanitizing and normalizing document paths."""

import re


def sanitize_filename(filename: str) -> str:
    sanitized = filename.strip()
    sanitized = re.sub(r'[\\/*?:"<>|]', "", sanitized)
    return sanitized


def ensure_md_extension(path: str) -> str:
    if not path.endswith(".md"):
        path += ".md"
    return path
