from unittest.mock import Mock

import pytest

from zk_chat.console_service import RichConsoleService
from zk_chat.services.link_traversal_service import ForwardLinkResult
from zk_chat.tools.find_forward_links import FindForwardLinks
from zk_chat.zettelkasten import Zettelkasten


class DescribeFindForwardLinks:
    """
    Tests for the FindForwardLinks tool which finds documents linked from a source document.
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
    def forward_links_tool(self, mock_zk, mock_console_service):
        return FindForwardLinks(mock_zk, mock_console_service)

    @pytest.fixture
    def mock_forward_link_results(self):
        return [
            ForwardLinkResult(
                source_document="concepts/systems-thinking.md",
                target_wikilink="Complex Systems",
                resolved_target="concepts/complex-systems.md",
                line_number=8,
                context_snippet="Building on [[Complex Systems]] theory, we can understand..."
            ),
            ForwardLinkResult(
                source_document="concepts/systems-thinking.md",
                target_wikilink="Feedback Loops",
                resolved_target="concepts/feedback-loops.md",
                line_number=15,
                context_snippet="The importance of [[Feedback Loops|feedback mechanisms]] cannot be overstated."
            )
        ]

    def should_be_instantiated_with_zettelkasten_and_console_service(self, mock_zk, mock_console_service):
        tool = FindForwardLinks(mock_zk, mock_console_service)

        assert isinstance(tool, FindForwardLinks)
        assert tool.zk == mock_zk
        assert tool.console_service == mock_console_service

    def should_use_default_console_service_when_none_provided(self, mock_zk):
        tool = FindForwardLinks(mock_zk)

        assert isinstance(tool, FindForwardLinks)
        assert tool.zk == mock_zk
        assert isinstance(tool.console_service, RichConsoleService)

    def should_return_error_message_when_document_does_not_exist(self, forward_links_tool, mock_zk):
        test_path = "nonexistent/document.md"
        mock_zk.document_exists.return_value = False

        result = forward_links_tool.run(test_path)

        mock_zk.document_exists.assert_called_once_with(test_path)
        assert result == f"Document not found at {test_path}"

    def should_find_forward_links_from_source_document(self, forward_links_tool, mock_zk, mock_forward_link_results):
        source = "concepts/systems-thinking.md"
        mock_zk.document_exists.return_value = True

        # Mock the LinkTraversalService's find_forward_links method
        forward_links_tool.link_service.find_forward_links = Mock(return_value=mock_forward_link_results)

        result = forward_links_tool.run(source)

        forward_links_tool.link_service.find_forward_links.assert_called_once_with(source)
        assert "concepts/complex-systems.md" in result
        assert "concepts/feedback-loops.md" in result
        assert "Complex Systems" in result
        assert "Feedback Loops" in result

    def should_handle_source_with_no_forward_links(self, forward_links_tool, mock_zk):
        source = "isolated/document.md"
        empty_results = []
        mock_zk.document_exists.return_value = True

        forward_links_tool.link_service.find_forward_links = Mock(return_value=empty_results)

        result = forward_links_tool.run(source)

        forward_links_tool.link_service.find_forward_links.assert_called_once_with(source)
        assert result == "[]"

    def should_return_json_formatted_forward_link_results(self, forward_links_tool, mock_zk, mock_forward_link_results):
        source = "test-document.md"
        mock_zk.document_exists.return_value = True

        forward_links_tool.link_service.find_forward_links = Mock(return_value=mock_forward_link_results)

        result = forward_links_tool.run(source)

        # Should be valid JSON representation of ForwardLinkResult objects
        assert "source_document" in result
        assert "target_wikilink" in result
        assert "resolved_target" in result
        assert "line_number" in result
        assert "context_snippet" in result

    def should_print_console_feedback_about_results_found(self, forward_links_tool, mock_zk, mock_console_service, mock_forward_link_results):
        source = "test-document.md"
        mock_zk.document_exists.return_value = True

        forward_links_tool.link_service.find_forward_links = Mock(return_value=mock_forward_link_results)

        forward_links_tool.run(source)

        # Should print informative message about results
        mock_console_service.print.assert_called_once()
        call_args = mock_console_service.print.call_args[0][0]
        assert "Found 2 forward links" in call_args
        assert source in call_args

    def should_handle_single_forward_link_result(self, forward_links_tool, mock_zk):
        source = "single-link.md"
        single_result = [
            ForwardLinkResult(
                source_document="single-link.md",
                target_wikilink="target-doc",
                resolved_target="references/target-doc.md",
                line_number=7,
                context_snippet="For more info see [[target-doc]] in the references."
            )
        ]
        mock_zk.document_exists.return_value = True

        forward_links_tool.link_service.find_forward_links = Mock(return_value=single_result)

        result = forward_links_tool.run(source)

        assert "references/target-doc.md" in result
        assert "target-doc" in result

    def should_handle_forward_links_with_context_snippets(self, forward_links_tool, mock_zk):
        source = "contextual-doc.md"
        contextual_results = [
            ForwardLinkResult(
                source_document="contextual-doc.md",
                target_wikilink="Deep Topic",
                resolved_target="deep/topic.md",
                line_number=12,
                context_snippet="To fully grasp this concept, we must explore [[Deep Topic]] in detail."
            )
        ]
        mock_zk.document_exists.return_value = True

        forward_links_tool.link_service.find_forward_links = Mock(return_value=contextual_results)

        result = forward_links_tool.run(source)

        assert "To fully grasp" in result
        assert "in detail" in result
        assert "Deep Topic" in result

    def should_handle_forward_links_with_captions(self, forward_links_tool, mock_zk):
        source = "captioned-links.md"
        caption_results = [
            ForwardLinkResult(
                source_document="captioned-links.md",
                target_wikilink="technical-guide",
                resolved_target="guides/technical-guide.md",
                line_number=20,
                context_snippet="Check out [[technical-guide|this excellent resource]] for implementation details."
            )
        ]
        mock_zk.document_exists.return_value = True

        forward_links_tool.link_service.find_forward_links = Mock(return_value=caption_results)

        result = forward_links_tool.run(source)

        assert "this excellent resource" in result
        assert "technical-guide" in result

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

        # Check that the parameter description explains the source document path
        source_param = params["properties"]["source_document"]
        assert "relative path" in source_param["description"]
        assert "source document" in source_param["description"]