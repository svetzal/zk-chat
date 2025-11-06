import pytest
from mojentic.llm.tools.llm_tool import LLMTool
from pytest_mock import MockerFixture

from zk_chat.tools.list_zk_images import ListZkImages
from zk_chat.zettelkasten import Zettelkasten


@pytest.fixture
def mock_zk(mocker: MockerFixture) -> Zettelkasten:
    mock_zk = mocker.Mock(spec=Zettelkasten)
    mock_zk.filesystem_gateway = mocker.Mock()
    return mock_zk


@pytest.fixture
def tool(mock_zk: Zettelkasten) -> LLMTool:
    return ListZkImages(mock_zk)


class DescribeListZkImages:
    """Tests for the ListZkImages tool which finds image files in the vault."""

    def should_be_instantiated_with_zettelkasten(self, mock_zk: Zettelkasten):
        tool = ListZkImages(mock_zk)

        assert isinstance(tool, ListZkImages)
        assert tool.zk is mock_zk

    def should_return_list_of_image_paths(self, tool: ListZkImages, mock_zk: Zettelkasten,
                                          mocker: MockerFixture):
        image_paths = [
            "images/photo1.jpg",
            "assets/diagram.png",
            "screenshots/screen.jpeg"
        ]
        iterate_mock = mocker.patch.object(mock_zk.filesystem_gateway,
                                           'iterate_files_by_extensions',
                                           return_value=iter(image_paths))

        result = tool.run()

        expected = "images/photo1.jpg\nassets/diagram.png\nscreenshots/screen.jpeg"
        assert result == expected
        iterate_mock.assert_called_once_with(['.jpg', '.jpeg', '.png'])

    def should_return_no_images_message_when_vault_has_no_images(self, tool: ListZkImages,
                                                                 mock_zk: Zettelkasten,
                                                                 mocker: MockerFixture):
        iterate_mock = mocker.patch.object(mock_zk.filesystem_gateway,
                                           'iterate_files_by_extensions', return_value=iter([]))

        result = tool.run()

        assert result == "No image files found in the vault."
        iterate_mock.assert_called_once_with(['.jpg', '.jpeg', '.png'])

    def should_have_correct_descriptor(self, tool: ListZkImages):
        descriptor = tool.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "list_images"
        assert "List all image file paths" in descriptor["function"]["description"]
        assert "JPG, JPEG, and PNG" in descriptor["function"]["description"]
        assert descriptor["function"]["parameters"]["type"] == "object"
        assert descriptor["function"]["parameters"]["properties"] == {}
        assert descriptor["function"]["parameters"]["required"] == []
