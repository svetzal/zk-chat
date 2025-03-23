import pytest

import structlog

from zk_chat.tools.git_gateway import GitGateway
from zk_chat.tools.uncommitted_changes import UncommittedChanges


@pytest.fixture
def mock_git_gateway(mocker):
    """Fixture for mocked GitGateway."""
    mock_instance = mocker.Mock(spec=GitGateway)
    return mock_instance


@pytest.fixture
def uncommitted_changes(mock_git_gateway):
    """Fixture for UncommittedChanges instance with mocked dependencies."""
    return UncommittedChanges("/mock/path", mock_git_gateway)


class DescribeUncommittedChanges:
    """
    Tests for the UncommittedChanges tool which retrieves uncommitted changes from a git repository.
    """
    def should_be_instantiated_with_base_path_and_git(self, mocker):
        """Test that UncommittedChanges can be instantiated with a base path and GitGateway."""
        base_path = "/test/path"
        mock_git = mocker.Mock(spec=GitGateway)

        tool = UncommittedChanges(base_path, mock_git)

        assert isinstance(tool, UncommittedChanges)
        assert tool.base_path == base_path
        assert tool.git == mock_git

    def should_return_error_message_when_adding_files_fails(self, uncommitted_changes, mock_git_gateway):
        """Test that run returns an error message when adding files fails."""
        mock_git_gateway.add_all_files.return_value = (False, "Error adding files")

        result = uncommitted_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        assert result == "Error adding files: Error adding files"

    def should_return_error_message_when_getting_diff_fails(self, uncommitted_changes, mock_git_gateway):
        """Test that run returns an error message when getting diff fails."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_diff.return_value = (False, "Error getting diff")

        result = uncommitted_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_diff.assert_called_once()
        assert result == "Error getting diff: Error getting diff"

    def should_return_no_changes_message_when_diff_is_empty(self, uncommitted_changes, mock_git_gateway):
        """Test that run returns a no changes message when diff is empty."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_diff.return_value = (True, "")

        result = uncommitted_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_diff.assert_called_once()
        assert result == "No uncommitted changes in the vault folder."

    def should_return_diff_output_when_changes_exist(self, uncommitted_changes, mock_git_gateway):
        """Test that run returns the diff output when changes exist."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_diff.return_value = (True, "diff --git a/file.txt b/file.txt")

        result = uncommitted_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_diff.assert_called_once()
        assert result == "Uncommitted changes in the vault folder:\ndiff --git a/file.txt b/file.txt"

    def should_handle_unexpected_exceptions(self, uncommitted_changes, mock_git_gateway, mocker):
        """Test that run handles unexpected exceptions."""
        mock_git_gateway.add_all_files.side_effect = Exception("Unexpected error")
        mock_logger = mocker.patch("zk_chat.tools.uncommitted_changes.logger")

        result = uncommitted_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_logger.error.assert_called_once()
        assert result == "Unexpected error getting uncommitted changes: Unexpected error"

    def should_have_correct_descriptor(self, uncommitted_changes):
        """Test that the descriptor property returns the correct value."""
        descriptor = uncommitted_changes.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "get_uncommitted_changes"
        assert "description" in descriptor["function"]
        assert descriptor["function"]["parameters"]["type"] == "object"
        assert "properties" in descriptor["function"]["parameters"]
        assert "required" in descriptor["function"]["parameters"]
