import pytest
from pytest_mock import MockerFixture

from zk_chat.models import ZkDocument
from zk_chat.tools.create_or_overwrite_zk_document import CreateOrOverwriteZkDocument


@pytest.fixture
def mock_zk(mocker: MockerFixture):
    return mocker.Mock()


@pytest.fixture
def write_tool(mock_zk):
    return CreateOrOverwriteZkDocument(mock_zk)


def test_write_document_happy_path(write_tool, mock_zk):
    title = "Path"
    metadata = {"title": "Test Document"}
    content = "# Test Content"

    result = write_tool.run(title=title, metadata=metadata, content=content)

    assert f"Successfully wrote to {title}.md" in result
    mock_zk.create_or_overwrite_document.assert_called_once()
    written_document = mock_zk.create_or_overwrite_document.call_args[0][0]
    assert isinstance(written_document, ZkDocument)
    assert written_document.relative_path == f"{title}.md"
    expected_metadata = metadata.copy()
    expected_metadata["reviewed"] = False
    assert written_document.metadata == expected_metadata
    assert written_document.content == content


def test_write_document_with_none_metadata(write_tool, mock_zk):
    title = "Path"
    metadata = None
    content = "# Test Content"

    result = write_tool.run(title=title, metadata=metadata, content=content)

    assert f"Successfully wrote to {title}.md" in result
    mock_zk.create_or_overwrite_document.assert_called_once()
    written_document = mock_zk.create_or_overwrite_document.call_args[0][0]
    assert isinstance(written_document, ZkDocument)
    assert written_document.relative_path == f"{title}.md"
    expected_metadata = {"reviewed": False}
    assert written_document.metadata == expected_metadata
    assert written_document.content == content


def test_write_document_with_non_dict_metadata(write_tool, mock_zk):
    title = "Path"
    metadata = "This is not a dictionary"
    content = "# Test Content"

    result = write_tool.run(title=title, metadata=metadata, content=content)

    assert f"Successfully wrote to {title}.md" in result
    mock_zk.create_or_overwrite_document.assert_called_once()
    written_document = mock_zk.create_or_overwrite_document.call_args[0][0]
    assert isinstance(written_document, ZkDocument)
    assert written_document.relative_path == f"{title}.md"
    expected_metadata = {"reviewed": False}
    assert written_document.metadata == expected_metadata
    assert written_document.content == content
