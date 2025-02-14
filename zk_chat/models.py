import os
import re

from pydantic import BaseModel


class ZkDocument(BaseModel):
    relative_path: str
    metadata: dict
    content: str

    @property
    def title(self) -> str:
        return self.strip_identifier_prefix(self.base_filename_without_extension())

    @property
    def id(self) -> str:
        return self.relative_path

    def strip_identifier_prefix(self, string):
        return re.sub(r'^[@!]\s*', '', string)

    def base_filename_without_extension(self):
        return os.path.splitext(os.path.basename(self.relative_path))[0]


class ZkDocumentChunk(BaseModel):
    document_id: str
    document_title: str
    text: str


class ZkQueryResult(BaseModel):
    chunk: ZkDocumentChunk
    distance: float
