import json
from unittest.mock import Mock

import pytest
from pydantic import BaseModel

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.tools.tool_helpers import (
    GitToolError,
    build_descriptor,
    check_document_exists,
    checked,
    format_model_results,
    log_and_return_error,
    tool_boundary,
)


class SimpleModel(BaseModel):
    name: str
    value: int


class DescribeChecked:
    def should_return_payload_on_success(self):
        result = checked((True, "ok"), "Error prefix")

        assert result == "ok"

    def should_raise_git_tool_error_on_failure(self):
        with pytest.raises(GitToolError) as exc_info:
            checked((False, "boom"), "Error getting diff")

        assert str(exc_info.value) == "Error getting diff: boom"


class DescribeLogAndReturnError:
    def should_call_logger_error_and_return_message(self):
        mock_logger = Mock()
        message = "Something went wrong"

        result = log_and_return_error(mock_logger, message)

        mock_logger.error.assert_called_once_with(message)
        assert result == message


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


class DescribeToolBoundary:
    def should_pass_through_return_value_on_success(self):
        @tool_boundary(OSError, "Error doing thing")
        def run():
            return "ok"

        assert run() == "ok"

    def should_return_error_string_when_exception_raised(self):
        @tool_boundary(OSError, "Error doing thing")
        def run():
            raise OSError("boom")

        result = run()

        assert "Error doing thing" in result
        assert "boom" in result

    def should_use_callable_prefix_with_runtime_args(self):
        @tool_boundary(OSError, lambda self, name: f"Error processing {name}")
        def run(self, name):
            raise OSError("failed")

        result = run(object(), "doc.md")

        assert "Error processing doc.md" in result

    def should_not_catch_unspecified_exception_types(self):
        @tool_boundary(OSError, "Error")
        def run():
            raise ValueError("unrelated")

        with pytest.raises(ValueError):
            run()


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
