import json
from unittest.mock import Mock

from pydantic import BaseModel

from zk_chat.services.document_service import DocumentService
from zk_chat.tools.tool_helpers import check_document_exists, format_model_results


class SimpleModel(BaseModel):
    name: str
    value: int


class DescribeFormatModelResults:
    def should_return_empty_json_array_for_empty_list(self):
        result = format_model_results([])

        assert result == "[]"

    def should_serialize_single_item_to_json_array(self):
        items = [SimpleModel(name="alpha", value=1)]

        result = format_model_results(items)

        parsed = json.loads(result)
        assert len(parsed) == 1
        assert parsed[0]["name"] == "alpha"
        assert parsed[0]["value"] == 1

    def should_serialize_multiple_items_preserving_order(self):
        items = [
            SimpleModel(name="first", value=1),
            SimpleModel(name="second", value=2),
        ]

        result = format_model_results(items)

        parsed = json.loads(result)
        assert len(parsed) == 2
        assert parsed[0]["name"] == "first"
        assert parsed[1]["name"] == "second"


class DescribeCheckDocumentExists:
    def should_return_none_when_document_exists(self):
        mock_document_service = Mock(spec=DocumentService)
        mock_document_service.document_exists.return_value = True

        result = check_document_exists(mock_document_service, "notes/doc.md")

        assert result is None

    def should_return_error_message_when_document_not_found(self):
        mock_document_service = Mock(spec=DocumentService)
        mock_document_service.document_exists.return_value = False

        result = check_document_exists(mock_document_service, "notes/missing.md")

        assert result == "Document not found at notes/missing.md"
