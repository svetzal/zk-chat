from pydantic import BaseModel, ConfigDict


class InitOptions(BaseModel):
    """Options for initializing the zk-chat session.

    Captures all configuration options passed to common_init as a typed,
    immutable model with sensible defaults. Callers only need to specify
    values that differ from the defaults.

    Attributes
    ----------
    vault : str | None
        Path to the vault directory. If None, resolved from bookmarks.
    save : bool
        Whether to save the vault path as a bookmark.
    gateway : str | None
        LLM gateway to use (e.g. "ollama", "openai"). If None, uses config value.
    model : str | None
        LLM model name. If None, uses config value.
    visual_model : str | None
        Visual model name for image analysis. If None, uses config value.
    reindex : bool
        Whether to reindex the vault on startup.
    full : bool
        Whether to perform a full reindex (vs incremental).
    unsafe : bool
        Whether to enable unsafe write/delete tools.
    git : bool
        Whether to enable git integration tools.
    store_prompt : bool
        Whether to store the system prompt in the vault.
    reset_memory : bool
        Whether to reset the smart memory on startup.
    """

    model_config = ConfigDict(frozen=True)

    vault: str | None = None
    save: bool = False
    gateway: str | None = None
    model: str | None = None
    visual_model: str | None = None
    reindex: bool = True
    full: bool = False
    unsafe: bool = False
    git: bool = False
    store_prompt: bool = True
    reset_memory: bool = False
