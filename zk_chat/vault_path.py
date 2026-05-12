"""Canonical vault path normalization.

All vault paths that are stored (bookmarks, config keys) or compared MUST be
passed through normalize_vault_path so the call sites cannot drift apart.
"""

from pathlib import Path


def normalize_vault_path(path: str | Path) -> str:
    """Return the canonical absolute, symlink-resolved form of a vault path."""
    return str(Path(path).expanduser().resolve())
