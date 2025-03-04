import pytest
from unittest.mock import Mock, patch
import os
from datetime import datetime

from zk_chat.models import ZkDocument
from zk_chat.zettelkasten import Zettelkasten

class DescribeZettelkasten:
    @pytest.fixture
    def mock_tokenizer_gateway(self):
        return Mock()

    @pytest.fixture
    def mock_vector_db(self):
        return Mock()

    @pytest.fixture
    def zk(self, mock_tokenizer_gateway, mock_vector_db):
        return Zettelkasten("test_root", mock_tokenizer_gateway, mock_vector_db)

    class DescribeAppendToDocument:
        def should_merge_metadata_dictionaries_recursively(self, zk):
            # Arrange
            original_doc = ZkDocument(
                relative_path="test.md",
                metadata={
                    "title": "Original",
                    "tags": ["tag1", "tag2"],
                    "nested": {
                        "key1": "value1",
                        "key2": {
                            "subkey1": "subvalue1"
                        }
                    }
                },
                content="Original content"
            )

            append_doc = ZkDocument(
                relative_path="test.md",
                metadata={
                    "tags": ["tag2", "tag3"],
                    "nested": {
                        "key2": {
                            "subkey2": "subvalue2"
                        },
                        "key3": "value3"
                    }
                },
                content="Appended content"
            )

            with patch.object(zk, 'read_document', return_value=original_doc), \
                 patch.object(zk, 'create_or_overwrite_document') as mock_write:

                # Act
                zk.append_to_document(append_doc)

                # Assert
                mock_write.assert_called_once()
                written_doc = mock_write.call_args[0][0]
                assert written_doc.metadata["title"] == "Original"
                assert set(written_doc.metadata["tags"]) == {"tag1", "tag2", "tag3"}
                assert written_doc.metadata["nested"]["key1"] == "value1"
                assert written_doc.metadata["nested"]["key2"]["subkey1"] == "subvalue1"
                assert written_doc.metadata["nested"]["key2"]["subkey2"] == "subvalue2"
                assert written_doc.metadata["nested"]["key3"] == "value3"

        def should_handle_none_and_empty_values_in_metadata(self, zk):
            # Arrange
            original_doc = ZkDocument(
                relative_path="test.md",
                metadata={
                    "title": "Original",
                    "empty_list": [],
                    "none_value": None,
                    "nested": {"key1": None}
                },
                content="Original content"
            )

            append_doc = ZkDocument(
                relative_path="test.md",
                metadata={
                    "empty_list": ["item1"],
                    "none_value": "value",
                    "nested": {"key1": "new_value"}
                },
                content="Appended content"
            )

            with patch.object(zk, 'read_document', return_value=original_doc), \
                 patch.object(zk, 'create_or_overwrite_document') as mock_write:

                # Act
                zk.append_to_document(append_doc)

                # Assert
                mock_write.assert_called_once()
                written_doc = mock_write.call_args[0][0]
                assert written_doc.metadata["empty_list"] == ["item1"]
                assert written_doc.metadata["none_value"] == "value"
                assert written_doc.metadata["nested"]["key1"] == "new_value"

        def should_handle_different_types_in_metadata(self, zk):
            # Arrange
            original_doc = ZkDocument(
                relative_path="test.md",
                metadata={
                    "value": "string",
                    "list": [1, 2, 3],
                    "nested": {"key": "value"}
                },
                content="Original content"
            )

            append_doc = ZkDocument(
                relative_path="test.md",
                metadata={
                    "value": ["new", "value"],  # string to list
                    "list": {"key": "value"},   # list to dict
                    "nested": "string"          # dict to string
                },
                content="Appended content"
            )

            with patch.object(zk, 'read_document', return_value=original_doc), \
                 patch.object(zk, 'create_or_overwrite_document') as mock_write:

                # Act
                zk.append_to_document(append_doc)

                # Assert
                mock_write.assert_called_once()
                written_doc = mock_write.call_args[0][0]
                assert written_doc.metadata["value"] == ["new", "value"]
                assert written_doc.metadata["list"] == {"key": "value"}
                assert written_doc.metadata["nested"] == "string"

        def should_properly_merge_content_and_metadata(self, zk):
            # Arrange
            original_doc = ZkDocument(
                relative_path="Document.md",
                metadata={
                    "tags": ["original"]
                },
                content="Original content here."
            )

            append_doc = ZkDocument(
                relative_path="Document.md",
                metadata={
                    "tags": ["appended"]
                },
                content="Appended content here."
            )

            with patch.object(zk, 'read_document', return_value=original_doc), \
                 patch.object(zk, 'create_or_overwrite_document') as mock_write:

                # Act
                zk.append_to_document(append_doc)

                # Assert
                mock_write.assert_called_once()
                written_doc = mock_write.call_args[0][0]

                # Verify metadata merging
                assert set(written_doc.metadata["tags"]) == {"original", "appended"}

                # Verify content merging
                expected_content = "Original content here.\n\n---\n\nAppended content here."
                assert written_doc.content == expected_content

                # Verify path preservation
                assert written_doc.relative_path == "Document.md"
