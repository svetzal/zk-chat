import json
from unittest.mock import Mock

from pydantic import BaseModel

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.tool_helpers import build_descriptor, check_document_exists, format_model_results


class SimpleModel(BaseModel):
    name: str
    value: int


class DescribeBuildDescriptor:
    def should_build_parameterless_descriptor(self):
        result = build_descriptor(name="my_tool", description="Does something.")

        assert result["type"] == "function"
        assert result["function"]["name"] == "my_tool"
        assert result["function"]["description"] == "Does something."
        assert result["function"]["parameters"]["type"] == "object"
        assert result["function"]["parameters"]["properties"] == {}
        assert result["function"]["parameters"]["required"] == []

    def should_build_descriptor_with_properties_and_required(self):
        properties = {"query": {"type": "string", "description": "A search query."}}

        result = build_descriptor(
            name="search", description="Search things.", properties=properties, required=["query"]
        )

        params = result["function"]["parameters"]
        assert params["properties"] == properties
        assert params["required"] == ["query"]
        assert "additionalProperties" not in params

    def should_include_additional_properties_when_specified(self):
        result = build_descriptor(name="create", description="Create doc.", additional_properties=False)

        assert result["function"]["parameters"]["additionalProperties"] is False

    def should_omit_additional_properties_when_not_specified(self):
        result = build_descriptor(name="list", description="List docs.")

        assert "additionalProperties" not in result["function"]["parameters"]


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
        mock_filesystem = Mock(spec=MarkdownFilesystemGateway)
        mock_filesystem.path_exists.return_value = True
        document_service = DocumentService(mock_filesystem)

        result = check_document_exists(document_service, "notes/doc.md")

        assert result is None

    def should_return_error_message_when_document_not_found(self):
        mock_filesystem = Mock(spec=MarkdownFilesystemGateway)
        mock_filesystem.path_exists.return_value = False
        document_service = DocumentService(mock_filesystem)

        result = check_document_exists(document_service, "notes/missing.md")

        assert result == "Document not found at notes/missing.md"
