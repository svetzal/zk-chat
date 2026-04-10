"""
Tests for the AnalyzeImage tool.
"""

from unittest.mock import Mock, patch

import pytest
from mojentic.llm import LLMBroker
from mojentic.llm.gateways import OllamaGateway
from mojentic.llm.gateways.models import LLMMessage, MessageRole

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.tools.analyze_image import AnalyzeImage


def _response(content: str) -> LLMMessage:
    return LLMMessage(role=MessageRole.Assistant, content=content)


class DescribeAnalyzeImage:
    """Tests for the AnalyzeImage LLM tool."""

    @pytest.fixture
    def mock_gateway(self):
        return Mock(spec=OllamaGateway)

    @pytest.fixture
    def mock_filesystem(self):
        return Mock(spec=MarkdownFilesystemGateway)

    @pytest.fixture
    def llm(self, mock_gateway):
        return LLMBroker(model="test-vision", gateway=mock_gateway)

    @pytest.fixture
    def analyze_tool(self, mock_filesystem, llm):
        return AnalyzeImage(mock_filesystem, llm)

    def should_return_not_found_message_when_image_missing(self, analyze_tool, mock_filesystem):
        mock_filesystem.path_exists.return_value = False

        result = analyze_tool.run("img/photo.png")

        assert result == "Image not found at img/photo.png"

    def should_not_call_gateway_when_image_missing(self, analyze_tool, mock_filesystem, mock_gateway):
        mock_filesystem.path_exists.return_value = False

        analyze_tool.run("missing.png")

        mock_gateway.complete.assert_not_called()

    def should_return_llm_analysis_when_image_exists(self, analyze_tool, mock_filesystem, mock_gateway):
        mock_filesystem.path_exists.return_value = True
        mock_filesystem.get_absolute_path_for_tool_access.return_value = "/abs/path/img.png"
        mock_gateway.complete.return_value = _response("A cat sitting on a desk")

        # MessageBuilder reads the image from disk, so we patch it at the module boundary
        # to avoid depending on a real image file in unit tests.
        with patch("zk_chat.tools.analyze_image.MessageBuilder") as mock_builder_class:
            mock_message = LLMMessage(role=MessageRole.User, content="describe image")
            mock_builder_class.return_value.add_image.return_value.build.return_value = mock_message

            result = analyze_tool.run("img/photo.png")

        assert result == "A cat sitting on a desk"
        mock_gateway.complete.assert_called_once()

    def should_have_correct_descriptor_name(self, analyze_tool):
        assert analyze_tool.descriptor["function"]["name"] == "analyze_image"

    def should_require_relative_path_parameter_in_descriptor(self, analyze_tool):
        assert "relative_path" in analyze_tool.descriptor["function"]["parameters"]["required"]
