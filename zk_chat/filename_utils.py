"""Pure filename utilities for sanitizing and normalizing document paths."""

import re


def sanitize_filename(filename: str) -> str:
    """Sanitize a string for use as a filename across operating systems.

    Strips leading/trailing whitespace and removes characters that are
    not allowed in filenames on Windows, macOS, or Linux.

    Parameters
    ----------
    filename : str
        The raw filename or title to sanitize.

    Returns
    -------
    str
        A sanitized filename safe to use on all major operating systems.
    """
    sanitized = filename.strip()
    sanitized = re.sub(r'[\\/*?:"<>|]', "", sanitized)
    return sanitized


def ensure_md_extension(path: str) -> str:
    """Ensure a path ends with the .md extension.

    Parameters
    ----------
    path : str
        The file path to check.

    Returns
    -------
    str
        The path with a .md extension appended if it was not already present.
    """
    if not path.endswith(".md"):
        path += ".md"
    return path
