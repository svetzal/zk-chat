import pytest

from mojentic.llm import LLMBroker
from mojentic.llm.gateways.models import LLMMessage
from pydantic import BaseModel

from zk_chat.tools.commit_changes import CommitChanges
from zk_chat.tools.git_gateway import GitGateway


@pytest.fixture
def mock_git_gateway(mocker):
    """Fixture for mocked GitGateway."""
    mock_instance = mocker.Mock(spec=GitGateway)
    return mock_instance


@pytest.fixture
def mock_llm_broker(mocker):
    """Fixture for mocked LLMBroker."""
    mock = mocker.Mock(spec=LLMBroker)
    return mock


@pytest.fixture
def commit_changes(mock_git_gateway, mock_llm_broker):
    """Fixture for CommitChanges instance with mocked dependencies."""
    return CommitChanges("/mock/path", mock_llm_broker, mock_git_gateway)


class DescribeCommitChanges:
    """
    Tests for the CommitChanges tool which commits changes in a git repository.
    """
    def should_be_instantiated_with_base_path_llm_and_git(self, mock_llm_broker, mocker):
        """Test that CommitChanges can be instantiated with a base path, LLM broker, and GitGateway."""
        base_path = "/test/path"
        mock_git = mocker.Mock(spec=GitGateway)

        tool = CommitChanges(base_path, mock_llm_broker, mock_git)

        assert isinstance(tool, CommitChanges)
        assert tool.base_path == base_path
        assert tool.llm == mock_llm_broker
        assert tool.git == mock_git

    def should_return_error_message_when_adding_files_fails(self, commit_changes, mock_git_gateway):
        """Test that run returns an error message when adding files fails."""
        mock_git_gateway.add_all_files.return_value = (False, "Error adding files")

        result = commit_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        assert result == "Error adding files: Error adding files"

    def should_return_error_message_when_checking_status_fails(self, commit_changes, mock_git_gateway):
        """Test that run returns an error message when checking status fails."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_status.return_value = (False, "Error checking status")

        result = commit_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_status.assert_called_once()
        assert result == "Error checking status: Error checking status"

    def should_return_no_changes_message_when_status_is_empty(self, commit_changes, mock_git_gateway):
        """Test that run returns a no changes message when status is empty."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_status.return_value = (True, "")

        result = commit_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_status.assert_called_once()
        assert result == "No changes to commit in the vault folder."

    def should_return_error_message_when_getting_diff_fails(self, commit_changes, mock_git_gateway):
        """Test that run returns an error message when getting diff fails."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_status.return_value = (True, "M file.txt")
        mock_git_gateway.get_diff.return_value = (False, "Error getting diff")

        result = commit_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_status.assert_called_once()
        mock_git_gateway.get_diff.assert_called_once()
        assert result == "Error getting diff: Error getting diff"

    def should_return_error_message_when_committing_fails(self, commit_changes, mock_git_gateway, mock_llm_broker, mocker):
        """Test that run returns an error message when committing fails."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_status.return_value = (True, "M file.txt")
        mock_git_gateway.get_diff.return_value = (True, "diff --git a/file.txt b/file.txt")

        mock_llm_broker.generate.return_value = "Test commit message"

        mock_git_gateway.commit.return_value = (False, "Error committing")

        result = commit_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_status.assert_called_once()
        mock_git_gateway.get_diff.assert_called_once()
        mock_llm_broker.generate.assert_called_once()
        mock_git_gateway.commit.assert_called_once_with("Test commit message")
        assert result == "Error committing changes: Error committing"

    def should_successfully_commit_changes(self, commit_changes, mock_git_gateway, mock_llm_broker, mocker):
        """Test that run successfully commits changes."""
        mock_git_gateway.add_all_files.return_value = (True, "Files added")
        mock_git_gateway.get_status.return_value = (True, "M file.txt")
        mock_git_gateway.get_diff.return_value = (True, "diff --git a/file.txt b/file.txt")

        mock_llm_broker.generate.return_value = "Test commit message"

        mock_git_gateway.commit.return_value = (True, "1 file changed")

        result = commit_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_git_gateway.get_status.assert_called_once()
        mock_git_gateway.get_diff.assert_called_once()
        mock_llm_broker.generate.assert_called_once()
        mock_git_gateway.commit.assert_called_once_with("Test commit message")
        assert result == "Successfully committed changes: 'Test commit message'"

    def should_generate_commit_message_using_llm(self, commit_changes, mock_llm_broker, mocker):
        """Test that _generate_commit_message uses the LLM to generate a commit message."""
        test_diff_summary = "diff --git a/file.txt b/file.txt"

        mock_llm_broker.generate.return_value = "Test commit message"

        result = commit_changes._generate_commit_message(test_diff_summary)

        mock_llm_broker.generate.assert_called_once()
        call_args = mock_llm_broker.generate.call_args[0][0]
        assert len(call_args) == 1
        assert isinstance(call_args[0], LLMMessage)
        assert test_diff_summary in call_args[0].content
        assert result == "Test commit message"

    def should_handle_unexpected_exceptions(self, commit_changes, mock_git_gateway, mocker):
        """Test that run handles unexpected exceptions."""
        mock_git_gateway.add_all_files.side_effect = Exception("Unexpected error")
        mock_logger = mocker.patch("zk_chat.tools.commit_changes.logger")

        result = commit_changes.run()

        mock_git_gateway.add_all_files.assert_called_once()
        mock_logger.error.assert_called_once()
        assert result == "Unexpected error committing changes: Unexpected error"

    def should_have_correct_descriptor(self, commit_changes):
        """Test that the descriptor property returns the correct value."""
        descriptor = commit_changes.descriptor

        assert descriptor["type"] == "function"
        assert descriptor["function"]["name"] == "commit_changes"
        assert "description" in descriptor["function"]
        assert descriptor["function"]["parameters"]["type"] == "object"
        assert "properties" in descriptor["function"]["parameters"]
        assert "required" in descriptor["function"]["parameters"]
