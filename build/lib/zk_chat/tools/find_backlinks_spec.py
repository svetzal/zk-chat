from unittest.mock import Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.services.link_traversal_service import BacklinkResult
from zk_chat.tools.find_backlinks import FindBacklinks
from zk_chat.zettelkasten import Zettelkasten


class DescribeFindBacklinks:
    """
    Tests for the FindBacklinks tool which finds documents that link to a target document.
    """

    @pytest.fixture
    def mock_zk(self):
        mock = Mock(spec=Zettelkasten)
        mock.filesystem_gateway = Mock()
        return mock

    @pytest.fixture
    def mock_console_service(self):
        return Mock(spec=RichConsoleService)

    @pytest.fixture
    def backlinks_tool(self, mock_zk, mock_console_service):
        return FindBacklinks(mock_zk, mock_console_service)

    @pytest.fixture
    def mock_backlink_results(self):
        return [
            BacklinkResult(
                linking_document="documents/intro.md",
                target_wikilink="Systems Thinking",
                resolved_target="concepts/systems-thinking.md",
                line_number=5,
                context_snippet="In this section we explore [[Systems Thinking]] as a core concept."
            ),
            BacklinkResult(
                linking_document="projects/analysis.md",
                target_wikilink="Systems Thinking",
                resolved_target="concepts/systems-thinking.md",
                line_number=12,
                context_snippet="The [[Systems Thinking|systems approach]] is fundamental here."
            )
        ]

    def should_be_instantiated_with_zettelkasten_and_console_service(self, mock_zk, mock_console_service):
        tool = FindBacklinks(mock_zk, mock_console_service)

        assert isinstance(tool, FindBacklinks)
        assert tool.zk == mock_zk
        assert tool.console_service == mock_console_service

    def should_use_default_console_service_when_none_provided(self, mock_zk):
        tool = FindBacklinks(mock_zk)

        assert isinstance(tool, FindBacklinks)
        assert tool.zk == mock_zk
        assert isinstance(tool.console_service, RichConsoleService)

    def should_find_backlinks_to_target_document(self, backlinks_tool, mock_backlink_results):
        target = "concepts/systems-thinking.md"

        # Mock the LinkTraversalService's find_backlinks method
        backlinks_tool.link_service.find_backlinks = Mock(return_value=mock_backlink_results)

        result = backlinks_tool.run(target)

        backlinks_tool.link_service.find_backlinks.assert_called_once_with(target)
        assert "documents/intro.md" in result
        assert "projects/analysis.md" in result
        assert "Systems Thinking" in result

    def should_find_backlinks_using_wikilink_text(self, backlinks_tool, mock_backlink_results):
        target = "Systems Thinking"

        backlinks_tool.link_service.find_backlinks = Mock(return_value=mock_backlink_results)

        result = backlinks_tool.run(target)

        backlinks_tool.link_service.find_backlinks.assert_called_once_with(target)
        assert "documents/intro.md" in result
        assert "projects/analysis.md" in result

    def should_handle_target_with_no_backlinks(self, backlinks_tool):
        target = "orphaned/document.md"
        empty_results = []

        backlinks_tool.link_service.find_backlinks = Mock(return_value=empty_results)

        result = backlinks_tool.run(target)

        backlinks_tool.link_service.find_backlinks.assert_called_once_with(target)
        assert result == "[]"

    def should_return_json_formatted_backlink_results(self, backlinks_tool, mock_backlink_results):
        target = "test-document.md"

        backlinks_tool.link_service.find_backlinks = Mock(return_value=mock_backlink_results)

        result = backlinks_tool.run(target)

        # Should be valid JSON representation of BacklinkResult objects
        assert "linking_document" in result
        assert "target_wikilink" in result
        assert "resolved_target" in result
        assert "line_number" in result
        assert "context_snippet" in result

    def should_print_console_feedback_about_results_found(self, backlinks_tool, mock_console_service, mock_backlink_results):
        target = "test-document.md"

        backlinks_tool.link_service.find_backlinks = Mock(return_value=mock_backlink_results)

        backlinks_tool.run(target)

        # Should print informative message about results
        mock_console_service.print.assert_called_once()
        call_args = mock_console_service.print.call_args[0][0]
        assert "Found 2 backlinks" in call_args
        assert target in call_args

    def should_handle_single_backlink_result(self, backlinks_tool):
        target = "single-reference.md"
        single_result = [
            BacklinkResult(
                linking_document="references/main.md",
                target_wikilink="single-reference",
                resolved_target="single-reference.md",
                line_number=3,
                context_snippet="See [[single-reference]] for details."
            )
        ]

        backlinks_tool.link_service.find_backlinks = Mock(return_value=single_result)

        result = backlinks_tool.run(target)

        assert "references/main.md" in result
        assert "single-reference" in result

    def should_handle_backlinks_with_context_snippets(self, backlinks_tool):
        target = "important-concept.md"
        contextual_results = [
            BacklinkResult(
                linking_document="analysis/deep-dive.md",
                target_wikilink="Important Concept",
                resolved_target="important-concept.md",
                line_number=8,
                context_snippet="Before we proceed, we must understand [[Important Concept]] thoroughly."
            )
        ]

        backlinks_tool.link_service.find_backlinks = Mock(return_value=contextual_results)

        result = backlinks_tool.run(target)

        assert "Before we proceed" in result
        assert "thoroughly" in result
        assert "Important Concept" in result

    def should_handle_backlinks_with_captions(self, backlinks_tool):
        target = "technical-topic.md"
        caption_results = [
            BacklinkResult(
                linking_document="overview/summary.md",
                target_wikilink="technical-topic",
                resolved_target="technical-topic.md",
                line_number=15,
                context_snippet="For more details see [[technical-topic|this comprehensive guide]]."
            )
        ]

        backlinks_tool.link_service.find_backlinks = Mock(return_value=caption_results)

        result = backlinks_tool.run(target)

        assert "comprehensive guide" in result
        assert "technical-topic" in result

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

        # Check that the parameter description explains both path and wikilink text options
        target_param = params["properties"]["target_document"]
        assert "relative path" in target_param["description"]
        assert "wikilink text" in target_param["description"]