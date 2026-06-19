"""Tests for the Qt GUI imperative shell."""

from unittest.mock import Mock, patch

import pytest
from mojentic.llm import ChatSession

from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.global_config import GlobalConfig
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.qt import ChatWorker, MainWindow, SettingsDialog, resolve_startup_config
from zk_chat.vault_path import normalize_vault_path

TEST_VAULT = normalize_vault_path("/tmp/zk_test_vault")
NEW_VAULT = normalize_vault_path("/tmp/zk_new_vault")


@pytest.fixture
def test_config():
    return Config(vault=TEST_VAULT, model="llama3", gateway=ModelGateway.OLLAMA)


@pytest.fixture
def mock_config_gateway(test_config):
    gateway = Mock(spec=ConfigGateway)
    gateway.load.return_value = test_config
    return gateway


@pytest.fixture
def test_global_config():
    gc = GlobalConfig()
    gc.add_bookmark(TEST_VAULT)
    gc.set_last_opened_bookmark(TEST_VAULT)
    return gc


@pytest.fixture
def mock_global_config_gateway(test_global_config):
    gateway = Mock(spec=GlobalConfigGateway)
    gateway.load.return_value = test_global_config
    return gateway


class DescribeChatWorker:
    def should_call_chat_session_send_with_query(self, qtbot):
        mock_session = Mock(spec=ChatSession)
        mock_session.send.return_value = "test response"
        worker = ChatWorker(mock_session, "test query")

        worker.run()

        mock_session.send.assert_called_once_with("test query")

    def should_emit_response_ready_with_session_response(self, qtbot):
        mock_session = Mock(spec=ChatSession)
        mock_session.send.return_value = "test response"
        worker = ChatWorker(mock_session, "test query")
        received = []
        worker.response_ready.connect(lambda r: received.append(r))

        worker.run()

        assert received == ["test response"]

    def should_emit_error_occurred_when_send_raises(self, qtbot):
        mock_session = Mock(spec=ChatSession)
        mock_session.send.side_effect = RuntimeError("LLM unreachable")
        worker = ChatWorker(mock_session, "test query")
        errors = []
        responses = []
        worker.error_occurred.connect(lambda m: errors.append(m))
        worker.response_ready.connect(lambda r: responses.append(r))

        worker.run()

        assert len(errors) == 1
        assert "LLM unreachable" in errors[0]
        assert responses == []


class DescribeSettingsDialog:
    @pytest.fixture
    def dialog(self, qtbot, test_config, mock_config_gateway, mock_global_config_gateway):
        with patch("zk_chat.qt.get_available_models", return_value=[]):
            dlg = SettingsDialog(test_config, mock_config_gateway, mock_global_config_gateway)
            qtbot.addWidget(dlg)
            return dlg

    def should_update_global_config_when_vault_changes(self, dialog, mock_config_gateway, mock_global_config_gateway):
        dialog.folder_edit.setText(NEW_VAULT)
        mock_config_gateway.load.return_value = None
        mock_global_config_gateway.load.return_value = GlobalConfig()

        with patch("zk_chat.qt.get_available_models", return_value=[]):
            dialog.save_settings()

        mock_global_config_gateway.load.assert_called_once()
        mock_global_config_gateway.save.assert_called_once()
        mock_config_gateway.save.assert_called_once()

    def should_not_update_global_config_when_vault_unchanged(
        self, dialog, mock_config_gateway, mock_global_config_gateway
    ):
        dialog.folder_edit.setText(TEST_VAULT)

        with patch("zk_chat.qt.get_available_models", return_value=[]):
            dialog.save_settings()

        mock_global_config_gateway.load.assert_not_called()
        mock_config_gateway.save.assert_called_once()


class DescribeResolveStartupConfig:
    def should_return_config_from_last_opened_bookmark(
        self, test_config, mock_config_gateway, mock_global_config_gateway
    ):
        result = resolve_startup_config(mock_config_gateway, mock_global_config_gateway, lambda: None)

        assert result == test_config
        mock_global_config_gateway.load.assert_called_once()
        mock_config_gateway.load.assert_called_once_with(TEST_VAULT)

    def should_not_save_global_config_when_bookmark_already_exists(
        self, test_config, mock_config_gateway, mock_global_config_gateway
    ):
        resolve_startup_config(mock_config_gateway, mock_global_config_gateway, lambda: None)

        mock_global_config_gateway.save.assert_not_called()

    def should_prompt_for_vault_when_no_bookmark_exists(self, test_config, mock_config_gateway):
        gc = GlobalConfig()
        gateway = Mock(spec=GlobalConfigGateway)
        gateway.load.return_value = gc
        mock_config_gateway.load.return_value = test_config
        prompt = Mock(return_value=TEST_VAULT)

        result = resolve_startup_config(mock_config_gateway, gateway, prompt)

        prompt.assert_called_once()
        assert result == test_config

    def should_save_global_config_when_vault_selected_by_user(self, test_config, mock_config_gateway):
        gc = GlobalConfig()
        gateway = Mock(spec=GlobalConfigGateway)
        gateway.load.return_value = gc
        mock_config_gateway.load.return_value = test_config

        resolve_startup_config(mock_config_gateway, gateway, lambda: TEST_VAULT)

        gateway.save.assert_called_once()

    def should_return_none_when_user_cancels_vault_prompt(self, mock_config_gateway):
        gc = GlobalConfig()
        gateway = Mock(spec=GlobalConfigGateway)
        gateway.load.return_value = gc

        result = resolve_startup_config(mock_config_gateway, gateway, lambda: None)

        assert result is None

    def should_save_vault_config_when_config_is_new(self, mock_config_gateway, mock_global_config_gateway):
        mock_config_gateway.load.return_value = None

        resolve_startup_config(mock_config_gateway, mock_global_config_gateway, lambda: None)

        mock_config_gateway.save.assert_called_once()

    def should_not_save_vault_config_when_config_already_exists(
        self, test_config, mock_config_gateway, mock_global_config_gateway
    ):
        resolve_startup_config(mock_config_gateway, mock_global_config_gateway, lambda: None)

        mock_config_gateway.save.assert_not_called()


class DescribeMainWindow:
    @pytest.fixture
    def mock_chat_session(self):
        return Mock(spec=ChatSession)

    @pytest.fixture
    def main_window(self, qtbot, test_config, mock_chat_session, mock_config_gateway, mock_global_config_gateway):
        window = MainWindow(test_config, mock_chat_session, mock_config_gateway, mock_global_config_gateway)
        qtbot.addWidget(window)
        return window

    def should_be_constructible_with_resolved_inputs(
        self, qtbot, test_config, mock_chat_session, mock_config_gateway, mock_global_config_gateway
    ):
        window = MainWindow(test_config, mock_chat_session, mock_config_gateway, mock_global_config_gateway)
        qtbot.addWidget(window)

        assert hasattr(window, "chat_input")
        assert hasattr(window, "scroll_area")
        assert window.chat_session is mock_chat_session

    def should_return_early_when_message_is_empty(self, main_window):
        main_window.chat_input.clear()

        main_window.send_message()

        assert not hasattr(main_window, "worker")

    def should_clear_input_after_sending_non_empty_message(self, main_window):
        main_window.chat_input.setText("test message")
        with patch("zk_chat.qt.ChatWorker") as mock_worker_class:
            mock_worker_class.return_value = Mock()

            main_window.send_message()

        assert main_window.chat_input.toPlainText() == ""

    def should_start_worker_when_message_is_non_empty(self, main_window):
        main_window.chat_input.setText("test message")
        with patch("zk_chat.qt.ChatWorker") as mock_worker_class:
            mock_worker_instance = Mock()
            mock_worker_class.return_value = mock_worker_instance

            main_window.send_message()

        mock_worker_instance.start.assert_called_once()

    def should_connect_error_occurred_signal_on_worker(self, main_window):
        main_window.chat_input.setText("test message")
        with patch("zk_chat.qt.ChatWorker") as mock_worker_class:
            mock_worker_instance = Mock()
            mock_worker_class.return_value = mock_worker_instance

            main_window.send_message()

        mock_worker_instance.error_occurred.connect.assert_called_once()

    def should_stop_spinner_and_show_error_on_show_assistant_error(self, qtbot, main_window):
        widget = main_window.append_message("Assistant", loading=True)

        main_window.show_assistant_error(widget, "LLM unreachable")

        assert not widget.spinner.isVisible()
        assert "Error" in widget.content_browser.toMarkdown()
