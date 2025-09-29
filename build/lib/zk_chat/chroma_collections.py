from enum import Enum


class ZkCollectionName(Enum):
    """
    Enumeration of collection names used in the Chroma vector database.

    This enum automatically converts to string when used in string contexts,
    so there's no need to explicitly call .value
    """
    EXCERPTS = "excerpts"
    DOCUMENTS = "documents"
    ZETTELKASTEN = "zettelkasten"  # deprecated
    SMART_MEMORY = "smart_memory"

    def __str__(self):
        return self.value
