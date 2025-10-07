"""
Vault builder for constructing test vaults from scenario specifications.

Creates isolated test vaults with documents and images for testing.
"""
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

if TYPE_CHECKING:
    from integration_tests.scenario_harness import Document, ImageFile


class VaultBuilder:
    """Builds test vaults from scenario specifications"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.vault_path = base_path / "test_vault"

    def build(
        self,
        documents: List["Document"],
        images: Optional[List["ImageFile"]] = None
    ) -> Path:
        """
        Build a test vault with specified documents and images.

        Returns path to created vault.
        """
        self.vault_path.mkdir(parents=True, exist_ok=True)

        for doc in documents:
            self._create_document(doc)

        if images:
            for img in images:
                self._copy_image(img)

        return self.vault_path

    def _create_document(self, doc: "Document"):
        """Create a document with optional frontmatter"""
        doc_path = self.vault_path / doc.path
        doc_path.parent.mkdir(parents=True, exist_ok=True)

        content = ""

        if doc.metadata:
            content += "---\n"
            for key, value in doc.metadata.items():
                if isinstance(value, list):
                    content += f"{key}:\n"
                    for item in value:
                        content += f"  - {item}\n"
                else:
                    content += f"{key}: {value}\n"
            content += "---\n\n"

        content += doc.content

        doc_path.write_text(content)

    def _copy_image(self, img: "ImageFile"):
        """Copy image file to vault"""
        dest_path = self.vault_path / img.path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        source_path = Path(__file__).parent / "test_resources" / img.source_path
        if not source_path.exists():
            raise FileNotFoundError(f"Test resource image not found: {source_path}")

        shutil.copy(source_path, dest_path)
