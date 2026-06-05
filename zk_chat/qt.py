import os
import sys

from mojentic.llm import ChatSession
from PySide6.QtCore import Qt, QThread, QTimer, Signal, Slot
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSplitter,
    QTextBrowser,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import zk_chat.bootstrap  # noqa: F401  # Sets CHROMA_TELEMETRY and logging before chromadb imports
from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway
from zk_chat.gateway_defaults import create_default_config_gateway, create_default_global_config_gateway
from zk_chat.global_config_gateway import GlobalConfigGateway
from zk_chat.model_selection import get_available_models
from zk_chat.qt_config_resolution import (
    resolve_config_for_vault,
    resolve_gui_vault_init,
    resolve_model_list_update,
    resolve_settings_change,
)
from zk_chat.tool_assembly import build_tools_from_config
from zk_chat.vault_path import normalize_vault_path


class LoadingSpinnerWidget(QWidget):
    """An indeterminate progress bar used to indicate a pending async operation."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setMinimum(0)
        self.progress.setMaximum(0)  # Makes it an "infinite" progress bar
        self.progress.setMaximumWidth(50)
        self.progress.setMinimumWidth(50)

        layout.addWidget(self.progress)


class ChatMessageWidget(QWidget):
    """A single chat message row displaying a role label alongside formatted content."""

    def __init__(self, role: str, content: str = "", loading: bool = False, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.role = role
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        role_label = QLabel(role)
        role_label.setFixedWidth(80)
        role_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        role_label.setStyleSheet("""
            font-weight: bold;
            color: #dddddd;
            padding: 5px;
        """)
        layout.addWidget(role_label)

        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.frame_layout = QHBoxLayout()
        self.frame_layout.setContentsMargins(5, 5, 5, 5)
        self.frame_layout.setSpacing(0)
        self.frame.setLayout(self.frame_layout)

        self.content_browser = QTextBrowser()
        self.content_browser.setOpenExternalLinks(True)
        self.content_browser.setFrameStyle(QFrame.NoFrame)
        self.content_browser.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.content_browser.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_browser.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.content_browser.setMinimumHeight(0)
        self.content_browser.document().setDocumentMargin(2)
        self.content_browser.setStyleSheet("""
            QTextBrowser {
                background-color: transparent;
                border: none;
                padding: 5px;
            }
        """)

        self.spinner = LoadingSpinnerWidget()
        self.spinner.setVisible(False)

        self.frame_layout.addWidget(self.content_browser)
        self.frame_layout.addWidget(self.spinner)

        if role.lower() == "user":
            self.frame.setStyleSheet("background-color: #222222; border-radius: 5px;")
        else:
            self.frame.setStyleSheet("background-color: #333333; border-radius: 5px;")

        layout.addWidget(self.frame)

        self.set_loading(loading)
        if not loading:
            self.set_content(content)

    def set_loading(self, loading: bool) -> None:
        self.spinner.setVisible(loading)
        self.content_browser.setVisible(not loading)
        if loading:
            self.content_browser.setMarkdown("")
            self.frame.setMinimumHeight(50)
            self.frame.setMaximumHeight(50)

    def set_content(self, content: str) -> None:
        self.content_browser.setMarkdown(content)
        self.content_browser.document().adjustSize()
        self.content_browser.document().setTextWidth(self.content_browser.viewport().width())
        doc_height = self.content_browser.document().size().height()
        # Add a small buffer to ensure all content is visible
        self.frame.setMinimumHeight(int(doc_height + 15))
        self.frame.setMaximumHeight(int(doc_height + 15))


class ChatWorker(QThread):
    """Background thread that sends a query to the chat session and emits the response."""

    response_ready = Signal(str)

    def __init__(self, chat_session: ChatSession, query: str) -> None:
        super().__init__()
        self.chat_session = chat_session
        self.query = query

    def run(self) -> None:
        """Send the query to the chat session and emit ``response_ready`` with the result."""
        response = self.chat_session.send(self.query)
        self.response_ready.emit(response)


def _add_labeled_field(parent_layout: QVBoxLayout, label_text: str, *widgets: QWidget) -> None:
    field_layout = QVBoxLayout()
    field_layout.addWidget(QLabel(label_text))
    for widget in widgets:
        field_layout.addWidget(widget)
    parent_layout.addLayout(field_layout)


class SettingsDialog(QDialog):
    """Modal dialog for editing vault path, model gateway, and model selections."""

    def __init__(
        self, config: Config, config_gateway: ConfigGateway, global_config_gateway: GlobalConfigGateway, parent=None
    ) -> None:
        super().__init__(parent)
        self.config = config
        self.config_gateway = config_gateway
        self.global_config_gateway = global_config_gateway
        self.setWindowTitle("Settings")
        self.setModal(True)

        layout = QVBoxLayout()

        self.folder_edit = QLineEdit(self.config.vault)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_folder)
        _add_labeled_field(layout, "Zettelkasten Folder:", self.folder_edit, browse_button)

        self.gateway_combo = QComboBox()
        self.gateway_combo.addItems([gateway.value for gateway in ModelGateway])
        current_gateway_index = self.gateway_combo.findText(self.config.gateway.value)
        if current_gateway_index >= 0:
            self.gateway_combo.setCurrentIndex(current_gateway_index)
        self.gateway_combo.currentIndexChanged.connect(self.update_model_list)
        _add_labeled_field(layout, "Model Gateway:", self.gateway_combo)

        self.chat_model_combo = QComboBox()
        _add_labeled_field(layout, "Chat Model:", self.chat_model_combo)

        self.visual_model_combo = QComboBox()
        self.visual_model_combo.addItem("None - Disable Visual Analysis")
        _add_labeled_field(layout, "Visual Analysis Model (optional):", self.visual_model_combo)

        self.update_model_list()

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def browse_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "Select Zettelkasten Folder")
        if folder:
            self.folder_edit.setText(folder)

    def update_model_list(self) -> None:
        """Refresh the chat and visual model combo boxes for the currently selected gateway."""
        gateway = ModelGateway(self.gateway_combo.currentText())
        api_key_present = bool(os.environ.get("OPENAI_API_KEY"))
        available_models = get_available_models(gateway)

        resolution = resolve_model_list_update(
            gateway=gateway,
            api_key_present=api_key_present,
            available_models=available_models,
            current_chat_model=self.config.model,
            current_visual_model=self.config.visual_model,
        )

        self.chat_model_combo.clear()
        self.chat_model_combo.addItems(resolution.chat_model_items)
        self.chat_model_combo.setCurrentIndex(resolution.chat_model_selected_index)

        self.visual_model_combo.clear()
        self.visual_model_combo.addItems(resolution.visual_model_items)
        self.visual_model_combo.setCurrentIndex(resolution.visual_model_selected_index)

    def save_settings(self) -> None:
        """Persist dialog selections to config and global config, then close the dialog."""
        new_vault_path = normalize_vault_path(self.folder_edit.text())
        new_gateway = ModelGateway(self.gateway_combo.currentText())
        new_chat_model = self.chat_model_combo.currentText()
        visual_model_text = self.visual_model_combo.currentText()

        loaded_config = None
        if new_vault_path != self.config.vault:
            loaded_config = self.config_gateway.load(new_vault_path)

        result = resolve_settings_change(
            current_config=self.config,
            new_vault_path=new_vault_path,
            new_gateway=new_gateway,
            new_chat_model=new_chat_model,
            visual_model_text=visual_model_text,
            loaded_config_for_new_vault=loaded_config,
        )

        if result.updated_global_config_needed:
            global_config = self.global_config_gateway.load()
            global_config.add_bookmark(new_vault_path)
            global_config.set_last_opened_bookmark(new_vault_path)
            self.global_config_gateway.save(global_config)

        self.config = result.updated_config
        self.config_gateway.save(self.config)
        self.accept()


class MainWindow(QMainWindow):
    """Primary application window containing the chat history and message input."""

    def __init__(self, config_gateway: ConfigGateway, global_config_gateway: GlobalConfigGateway) -> None:
        super().__init__()
        self.config_gateway = config_gateway
        self.global_config_gateway = global_config_gateway

        global_config = self.global_config_gateway.load()
        last_opened = global_config.get_last_opened_bookmark_path()

        user_selected = None
        if not last_opened:
            user_selected = QFileDialog.getExistingDirectory(
                self, "Select Your Zettelkasten Vault Directory", os.path.expanduser("~")
            )
            if not user_selected:
                sys.exit(0)
            user_selected = normalize_vault_path(user_selected)

        vault_init = resolve_gui_vault_init(last_opened, user_selected)

        if vault_init.needs_bookmark_update:
            global_config.add_bookmark(vault_init.vault_path)
            global_config.set_last_opened_bookmark(vault_init.vault_path)
            self.global_config_gateway.save(global_config)

        loaded_config = self.config_gateway.load(vault_init.vault_path)
        self.config, was_created = resolve_config_for_vault(loaded_config, vault_init.vault_path)
        if was_created:
            self.config_gateway.save(self.config)

        self.chat_session = None
        self.initialize_chat_session()

        self.setWindowTitle("Zk-Chat")
        self.setMinimumSize(800, 600)

        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")
        settings_action = settings_menu.addAction("Configure...")
        settings_action.triggered.connect(self.show_settings)

        splitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(splitter)

        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(15)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        top_layout.addWidget(self.scroll_area)
        splitter.addWidget(top_widget)

        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(10)  # Add spacing between elements

        self.chat_input = QTextEdit()
        self.chat_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        send_button = QPushButton("Send")
        send_button.setMinimumWidth(80)  # Set minimum width
        send_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        send_button.clicked.connect(self.send_message)

        bottom_layout.addWidget(self.chat_input)
        bottom_layout.addWidget(send_button, alignment=Qt.AlignVCenter)  # Align vertically
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(bottom_widget)

        splitter.setSizes([400, 200])

    def initialize_chat_session(self) -> None:
        """Build a fresh ``ChatSession`` from the current vault config, replacing any prior session."""
        components = build_tools_from_config(self.config)
        self.chat_session = ChatSession(
            components.llm_broker,
            system_prompt=components.system_prompt,
            tools=components.tools,
        )

    def show_settings(self) -> None:
        dialog = SettingsDialog(self.config, self.config_gateway, self.global_config_gateway, self)
        if dialog.exec():
            self.config = dialog.config
            self.initialize_chat_session()

    def append_message(self, role: str, content: str = "", loading: bool = False) -> ChatMessageWidget:
        """Add a new message widget to the chat history and scroll to it.

        Parameters
        ----------
        role : str
            Display label for the message sender (e.g. ``"User"`` or ``"Assistant"``).
        content : str
            Markdown-formatted message body (ignored when ``loading`` is ``True``).
        loading : bool
            When ``True``, show a spinner instead of content until updated.

        Returns
        -------
        ChatMessageWidget
            The newly added widget, which callers can later update via ``set_content``.
        """
        if self.messages_layout.count() > 0:
            stretch_item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
            if stretch_item.spacerItem():
                self.messages_layout.removeItem(stretch_item)

        message_widget = ChatMessageWidget(role, content, loading)
        self.messages_layout.addWidget(message_widget)

        self.messages_layout.addStretch()

        QTimer.singleShot(
            1, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        )

        return message_widget

    @Slot()
    def send_message(self) -> None:
        """Read the input field, display the user message, and start a background ``ChatWorker``."""
        message = self.chat_input.toPlainText().strip()
        if not message:
            return

        self.append_message("User", message)
        self.chat_input.clear()

        assistant_widget = self.append_message("Assistant", loading=True)

        self.worker = ChatWorker(self.chat_session, message)
        self.worker.response_ready.connect(lambda response: self.update_assistant_response(assistant_widget, response))
        self.worker.start()

    def update_assistant_response(self, widget: ChatMessageWidget, response: str) -> None:
        """Replace the loading spinner on ``widget`` with the LLM response text."""
        widget.set_loading(False)
        widget.set_content(response)
        # Ensure we scroll to see the complete response
        QTimer.singleShot(
            1, lambda: self.scroll_area.verticalScrollBar().setValue(self.scroll_area.verticalScrollBar().maximum())
        )


def main() -> None:
    """Application entry point: create the Qt app, build the main window, and start the event loop."""
    app = QApplication(sys.argv)
    config_gateway = create_default_config_gateway()
    global_config_gateway = create_default_global_config_gateway()
    window = MainWindow(config_gateway, global_config_gateway)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
