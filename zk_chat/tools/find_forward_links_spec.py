from unittest.mock import Mock

import pytest

from zk_chat.console_service import ConsoleGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.document_service import DocumentService
from zk_chat.services.link_traversal_service import ForwardLinkResult, LinkTraversalService
from zk_chat.tools.find_forward_links import FindForwardLinks
from zk_chat.tools.tool_helpers import format_model_results


class DescribeFormatForwardLinkResults:
    """Tests for the format_model_results function with ForwardLinkResult objects."""

    def should_return_empty_list_string_for_no_results(self):
        result = format_model_results([])

        assert result == "[]"

    def should_serialize_single_forward_link_result(self):
        results = [
            ForwardLinkResult(
                source_document="notes/intro.md",
                target_wikilink="Main Topic",
                resolved_target="concepts/main.md",
                line_number=5,
                context_snippet="See [[Main Topic]] for more.",
            )
        ]

        result = format_model_results(results)

        assert "notes/intro.md" in result
        assert "Main Topic" in result
        assert "concepts/main.md" in result

    def should_serialize_multiple_forward_link_results(self):
        results = [
            ForwardLinkResult(
                source_document="doc.md",
                target_wikilink="TopicA",
                resolved_target="a.md",
                line_number=1,
                context_snippet="[[TopicA]] first.",
            ),
            ForwardLinkResult(
                source_document="doc.md",
                target_wikilink="TopicB",
                resolved_target="b.md",
                line_number=2,
                context_snippet="[[TopicB]] second.",
            ),
        ]

        result = format_model_results(results)

        assert "a.md" in result
        assert "b.md" in result


def _make_services_for_forward_links(
    source: str, forward_link_results: list[ForwardLinkResult]
) -> tuple[DocumentService, LinkTraversalService, Mock]:
    """
    Build real DocumentService and LinkTraversalService instances whose filesystem
    mock is configured to produce the desired forward link results when scanned.
    """
    mock_filesystem = Mock(spec=MarkdownFilesystemGateway)

    snippet_content = "\n".join(r.context_snippet for r in forward_link_results)

    def path_exists(path):
        return path == source

    mock_filesystem.path_exists.side_effect = path_exists

    def read_markdown(path):
        if path == source:
            return ({}, snippet_content)
        raise FileNotFoundError(path)

    mock_filesystem.read_markdown.side_effect = read_markdown

    def resolve_wikilink(wikilink_str):
        wikilink_title = wikilink_str.lstrip("[").rstrip("]").split("|")[0]
        for r in forward_link_results:
            if r.target_wikilink == wikilink_title or r.target_wikilink in wikilink_str:
                return r.resolved_target
        raise ValueError(f"Cannot resolve {wikilink_str}")

    mock_filesystem.resolve_wikilink.side_effect = resolve_wikilink

    document_service = DocumentService(mock_filesystem)
    link_service = LinkTraversalService(mock_filesystem)
    return document_service, link_service, mock_filesystem


class DescribeFindForwardLinks:
    """
    Tests for the FindForwardLinks tool which finds documents linked from a source document.
    """

    @pytest.fixture
    def mock_console_service(self):
        return Mock(spec=ConsoleGateway)

    @pytest.fixture
    def forward_link_results(self):
        return [
            ForwardLinkResult(
                source_document="concepts/systems-thinking.md",
                target_wikilink="Complex Systems",
                resolved_target="concepts/complex-systems.md",
                line_number=8,
                context_snippet="Building on [[Complex Systems]] theory, we can understand...",
            ),
            ForwardLinkResult(
                source_document="concepts/systems-thinking.md",
                target_wikilink="Feedback Loops",
                resolved_target="concepts/feedback-loops.md",
                line_number=15,
                context_snippet="The importance of [[Feedback Loops|feedback mechanisms]] cannot be overstated.",
            ),
        ]

    @pytest.fixture
    def source(self):
        return "concepts/systems-thinking.md"

    @pytest.fixture
    def services(self, source, forward_link_results):
        return _make_services_for_forward_links(source, forward_link_results)

    @pytest.fixture
    def forward_links_tool(self, services, mock_console_service):
        document_service, link_service, _ = services
        return FindForwardLinks(document_service, link_service, mock_console_service)

    def should_be_instantiated_with_services_and_console_service(
        self, services, mock_console_service
    ):
        document_service, link_service, _ = services
        tool = FindForwardLinks(document_service, link_service, mock_console_service)

        assert isinstance(tool, FindForwardLinks)
        assert tool.document_service is document_service
        assert tool.link_service == link_service
        assert tool.console_service == mock_console_service

    def should_return_error_message_when_document_does_not_exist(self, mock_console_service):
        mock_filesystem = Mock(spec=MarkdownFilesystemGateway)
        mock_filesystem.path_exists.return_value = False
        document_service = DocumentService(mock_filesystem)
        link_service = LinkTraversalService(mock_filesystem)
        tool = FindForwardLinks(document_service, link_service, mock_console_service)
        test_path = "nonexistent/document.md"

        result = tool.run(test_path)

        mock_filesystem.path_exists.assert_called_once_with(test_path)
        assert result == f"Document not found at {test_path}"

    def should_find_forward_links_from_source_document(
        self, forward_links_tool, source
    ):
        result = forward_links_tool.run(source)

        assert "concepts/complex-systems.md" in result
        assert "concepts/feedback-loops.md" in result
        assert "Complex Systems" in result
        assert "Feedback Loops" in result

    def should_handle_source_with_no_forward_links(self, mock_console_service):
        mock_filesystem = Mock(spec=MarkdownFilesystemGateway)
        mock_filesystem.path_exists.return_value = True
        mock_filesystem.read_markdown.return_value = ({}, "No wikilinks here.")
        document_service = DocumentService(mock_filesystem)
        link_service = LinkTraversalService(mock_filesystem)
        tool = FindForwardLinks(document_service, link_service, mock_console_service)

        result = tool.run("isolated/document.md")

        assert result == "[]"

    def should_return_json_formatted_forward_link_results(
        self, forward_links_tool, source
    ):
        result = forward_links_tool.run(source)

        assert "source_document" in result
        assert "target_wikilink" in result
        assert "resolved_target" in result
        assert "line_number" in result
        assert "context_snippet" in result

    def should_print_console_feedback_about_results_found(
        self, forward_links_tool, mock_console_service, source
    ):
        forward_links_tool.run(source)

        mock_console_service.print.assert_called_once()
        call_args = mock_console_service.print.call_args[0][0]
        assert "Found 2 forward links" in call_args
        assert source in call_args

    def should_have_correct_descriptor_for_llm_integration(self, forward_links_tool):
        descriptor = forward_links_tool.descriptor

        assert descriptor["type"] == "function"
        function_def = descriptor["function"]
        assert function_def["name"] == "find_forward_links"
        assert "find all documents that are linked from" in function_def["description"].lower()

        params = function_def["parameters"]
        assert params["type"] == "object"
        assert "source_document" in params["properties"]
        assert params["required"] == ["source_document"]

        source_param = params["properties"]["source_document"]
        assert "relative path" in source_param["description"]
        assert "source document" in source_param["description"]
