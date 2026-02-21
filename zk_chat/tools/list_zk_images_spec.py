from unittest.mock import Mock

import pytest
from mojentic.llm.tools.llm_tool import LLMTool

from zk_chat.markdown.markdown_filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.tools.list_zk_images import ListZkImages


@pytest.fixture
def mock_filesystem():
    return Mock(spec=MarkdownFilesystemGateway)


@pytest.fixture
def tool(mock_filesystem) -> LLMTool:
    return ListZkImages(mock_filesystem)


class DescribeListZkImages:
    """Tests for the ListZkImages tool which finds image files in the vault."""

    def should_be_instantiated_with_filesystem_gateway(self, mock_filesystem):
        tool = ListZkImages(mock_filesystem)

        assert isinstance(tool, ListZkImages)
        assert tool.fs is mock_filesystem

    def should_return_list_of_image_paths(self, tool: ListZkImages, mock_filesystem):
        image_paths = ["images/photo1.jpg", "assets/diagram.png", "screenshots/screen.jpeg"]
        mock_filesystem.iterate_files_by_extensions.return_value = iter(image_paths)

        result = tool.run()

        expected = "images/photo1.jpg\nassets/diagram.png\nscreenshots/screen.jpeg"
        assert result == expected
        mock_filesystem.iterate_files_by_extensions.assert_called_once_with([".jpg", ".jpeg", ".png"])

    def should_return_no_images_message_when_vault_has_no_images(self, tool: ListZkImages, mock_filesystem):
        mock_filesystem.iterate_files_by_extensions.return_value = iter([])

        result = tool.run()

        assert result == "No image files found in the vault."
        mock_filesystem.iterate_files_by_extensions.assert_called_once_with([".jpg", ".jpeg", ".png"])

    def should_have_correct_descriptor(self, tool: ListZkImages):
        descriptor = tool.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "list_images"
        assert "List all image file paths" in descriptor["function"]["description"]
        assert "JPG, JPEG, and PNG" in descriptor["function"]["description"]
        assert descriptor["function"]["parameters"]["type"] == "object"
        assert descriptor["function"]["parameters"]["properties"] == {}
        assert descriptor["function"]["parameters"]["required"] == []
