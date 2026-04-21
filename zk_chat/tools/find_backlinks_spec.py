from unittest.mock import Mock

import pytest

from zk_chat.console_service import ConsoleGateway
from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.services.link_traversal_service import BacklinkResult, LinkTraversalService
from zk_chat.tools.find_backlinks import FindBacklinks
from zk_chat.tools.tool_helpers import format_model_results


class DescribeFormatBacklinkResults:
    """Tests for the format_model_results function with BacklinkResult objects."""

    def should_return_empty_list_string_for_no_results(self):
        result = format_model_results([])

        assert result == "[]"

    def should_serialize_single_backlink_result(self):
        results = [
            BacklinkResult(
                linking_document="notes/intro.md",
                target_wikilink="Main Topic",
                resolved_target="concepts/main.md",
                line_number=3,
                context_snippet="See [[Main Topic]] for details.",
            )
        ]

        result = format_model_results(results)

        assert "notes/intro.md" in result
        assert "Main Topic" in result
        assert "concepts/main.md" in result

    def should_serialize_multiple_backlink_results(self):
        results = [
            BacklinkResult(
                linking_document="doc1.md",
                target_wikilink="Topic",
                resolved_target="topic.md",
                line_number=1,
                context_snippet="[[Topic]] mentioned here.",
            ),
            BacklinkResult(
                linking_document="doc2.md",
                target_wikilink="Topic",
                resolved_target="topic.md",
                line_number=2,
                context_snippet="Also [[Topic]] here.",
            ),
        ]

        result = format_model_results(results)

        assert "doc1.md" in result
        assert "doc2.md" in result


def _make_link_service_with_backlinks(target: str, backlink_results: list[BacklinkResult]) -> LinkTraversalService:
    """
    Build a real LinkTraversalService whose filesystem mock returns content
    that, when scanned, produces the desired backlink results.
    """
    mock_filesystem = Mock(spec=MarkdownFilesystemGateway)

    linking_docs = list({r.linking_document for r in backlink_results})
    mock_filesystem.iterate_markdown_files.return_value = linking_docs

    def path_exists(path):
        return path in linking_docs

    mock_filesystem.path_exists.side_effect = path_exists

    def read_markdown(path):
        snippets = [r.context_snippet for r in backlink_results if r.linking_document == path]
        content = "\n".join(snippets)
        return ({}, content)

    mock_filesystem.read_markdown.side_effect = read_markdown

    def resolve_wikilink(wikilink_str):
        wikilink_title = wikilink_str.lstrip("[").rstrip("]").split("|")[0]
        for r in backlink_results:
            if r.target_wikilink in wikilink_str or wikilink_title in r.target_wikilink:
                return target
        raise ValueError(f"Cannot resolve {wikilink_str}")

    mock_filesystem.resolve_wikilink.side_effect = resolve_wikilink

    return LinkTraversalService(mock_filesystem)


class DescribeFindBacklinks:
    """
    Tests for the FindBacklinks tool which finds documents that link to a target document.
    """

    @pytest.fixture
    def mock_console_service(self):
        return Mock(spec=ConsoleGateway)

    @pytest.fixture
    def backlink_results(self):
        return [
            BacklinkResult(
                linking_document="documents/intro.md",
                target_wikilink="Systems Thinking",
                resolved_target="concepts/systems-thinking.md",
                line_number=5,
                context_snippet="In this section we explore [[Systems Thinking]] as a core concept.",
            ),
            BacklinkResult(
                linking_document="projects/analysis.md",
                target_wikilink="Systems Thinking",
                resolved_target="concepts/systems-thinking.md",
                line_number=12,
                context_snippet="The [[Systems Thinking|systems approach]] is fundamental here.",
            ),
        ]

    @pytest.fixture
    def target(self):
        return "concepts/systems-thinking.md"

    @pytest.fixture
    def link_service(self, target, backlink_results):
        return _make_link_service_with_backlinks(target, backlink_results)

    @pytest.fixture
    def backlinks_tool(self, link_service, mock_console_service):
        return FindBacklinks(link_service, mock_console_service)

    def should_be_instantiated_with_link_service_and_console_service(self, link_service, mock_console_service):
        tool = FindBacklinks(link_service, mock_console_service)

        assert isinstance(tool, FindBacklinks)
        assert tool.link_service == link_service
        assert tool.console_service == mock_console_service

    def should_find_backlinks_to_target_document(self, backlinks_tool, target):
        result = backlinks_tool.run(target)

        assert "documents/intro.md" in result
        assert "projects/analysis.md" in result
        assert "Systems Thinking" in result

    def should_handle_target_with_no_backlinks(self, mock_console_service):
        mock_filesystem = Mock(spec=MarkdownFilesystemGateway)
        mock_filesystem.iterate_markdown_files.return_value = []
        link_service = LinkTraversalService(mock_filesystem)
        tool = FindBacklinks(link_service, mock_console_service)

        result = tool.run("orphaned/document.md")

        assert result == "[]"

    def should_return_json_formatted_backlink_results(self, backlinks_tool, target):
        result = backlinks_tool.run(target)

        assert "linking_document" in result
        assert "target_wikilink" in result
        assert "resolved_target" in result
        assert "line_number" in result
        assert "context_snippet" in result

    def should_print_console_feedback_about_results_found(self, backlinks_tool, mock_console_service, target):
        backlinks_tool.run(target)

        mock_console_service.tool_info.assert_called_once()
        call_args = mock_console_service.tool_info.call_args[0][0]
        assert "Found 2 backlinks" in call_args
        assert target in call_args

    def should_handle_backlinks_with_context_snippets(self, mock_console_service):
        target = "important-concept.md"
        contextual_results = [
            BacklinkResult(
                linking_document="analysis/deep-dive.md",
                target_wikilink="Important Concept",
                resolved_target=target,
                line_number=8,
                context_snippet="Before we proceed, we must understand [[Important Concept]] thoroughly.",
            )
        ]
        link_service = _make_link_service_with_backlinks(target, contextual_results)
        tool = FindBacklinks(link_service, mock_console_service)

        result = tool.run(target)

        assert "Before we proceed" in result
        assert "thoroughly" in result
        assert "Important Concept" in result

    def should_have_correct_descriptor_for_llm_integration(self, backlinks_tool):
        descriptor = backlinks_tool.descriptor

        assert descriptor["type"] == "function"
        function_def = descriptor["function"]
        assert function_def["name"] == "find_backlinks"
        assert "find all documents that contain wikilinks pointing to" in function_def["description"].lower()

        params = function_def["parameters"]
        assert params["type"] == "object"
        assert "target_document" in params["properties"]
        assert params["required"] == ["target_document"]

        target_param = params["properties"]["target_document"]
        assert "relative path" in target_param["description"]
        assert "wikilink text" in target_param["description"]
