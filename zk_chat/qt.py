import sys

from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QTextEdit, QPushButton, QDialog, QFrame,
                               QLabel, QLineEdit, QComboBox, QFileDialog, QSplitter, QHBoxLayout, QSizePolicy,
                               QTextBrowser, QScrollArea, QProgressBar)
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
from mojentic.llm.tools.date_resolver import ResolveDateTool

from zk_chat.chat import ChatSession, LLMBroker, ChromaGateway, Zettelkasten
from zk_chat.config import Config, get_available_models
from zk_chat.filesystem_gateway import FilesystemGateway
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.vector_database import VectorDatabase


class LoadingSpinnerWidget(QWidget):
    def __init__(self, parent=None):
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
    def __init__(self, role: str, content: str = "", loading: bool = False, parent=None):
        super().__init__(parent)
        self.role = role
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        # Role label on the left
        role_label = QLabel(role)
        role_label.setFixedWidth(80)
        role_label.setAlignment(Qt.AlignTop | Qt.AlignRight)
        role_label.setStyleSheet("""
            font-weight: bold;
            color: #dddddd;
            padding: 5px;
        """)
        layout.addWidget(role_label)

        # Frame for content
        self.frame = QFrame()
        self.frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.frame_layout = QHBoxLayout()
        self.frame_layout.setContentsMargins(5, 5, 5, 5)
        self.frame_layout.setSpacing(0)
        self.frame.setLayout(self.frame_layout)

        # Content browser
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

        # Loading spinner
        self.spinner = LoadingSpinnerWidget()
        self.spinner.setVisible(False)

        # Add widgets to frame
        self.frame_layout.addWidget(self.content_browser)
        self.frame_layout.addWidget(self.spinner)

        # Set different background colors for user and assistant
        if role.lower() == "user":
            self.frame.setStyleSheet("background-color: #222222; border-radius: 5px;")
        else:
            self.frame.setStyleSheet("background-color: #333333; border-radius: 5px;")

        layout.addWidget(self.frame)

        # Set initial state
        self.set_loading(loading)
        if not loading:
            self.set_content(content)

    def set_loading(self, loading: bool):
        self.spinner.setVisible(loading)
        self.content_browser.setVisible(not loading)
        if loading:
            self.content_browser.setMarkdown("")
            self.frame.setMinimumHeight(50)
            self.frame.setMaximumHeight(50)

    def set_content(self, content: str):
        self.content_browser.setMarkdown(content)
        self.content_browser.document().adjustSize()
        self.content_browser.document().setTextWidth(self.content_browser.viewport().width())
        doc_height = self.content_browser.document().size().height()
        # Add a small buffer to ensure all content is visible
        self.frame.setMinimumHeight(int(doc_height + 15))
        self.frame.setMaximumHeight(int(doc_height + 15))


class ChatWorker(QThread):
    response_ready = Signal(str)

    def __init__(self, chat_session: ChatSession, query: str):
        super().__init__()
        self.chat_session = chat_session
        self.query = query

    def run(self):
        response = self.chat_session.send(self.query)
        self.response_ready.emit(response)


class SettingsDialog(QDialog):
    def __init__(self, config: Config, parent=None):
        super().__init__(parent)
        self.config = config
        self.setWindowTitle("Settings")
        self.setModal(True)

        layout = QVBoxLayout()

        # Zettelkasten folder selection
        folder_layout = QVBoxLayout()
        folder_label = QLabel("Zettelkasten Folder:")
        self.folder_edit = QLineEdit(self.config.vault)
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_folder)
        folder_layout.addWidget(folder_label)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(browse_button)
        layout.addLayout(folder_layout)

        # Model selection
        model_layout = QVBoxLayout()
        model_label = QLabel("LLM Model:")
        self.model_combo = QComboBox()
        available_models = get_available_models()
        self.model_combo.addItems(available_models)
        current_index = self.model_combo.findText(self.config.model)
        if current_index >= 0:
            self.model_combo.setCurrentIndex(current_index)
        model_layout.addWidget(model_label)
        model_layout.addWidget(self.model_combo)
        layout.addLayout(model_layout)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Zettelkasten Folder")
        if folder:
            self.folder_edit.setText(folder)

    def save_settings(self):
        self.config.vault = self.folder_edit.text()
        self.config.model = self.model_combo.currentText()
        self.config.save()
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = Config.load_or_initialize()
        self.chat_session = None
        self.initialize_chat_session()

        self.setWindowTitle("ZK-RAG Chat")
        self.setMinimumSize(800, 600)

        # Create menu bar
        menubar = self.menuBar()
        settings_menu = menubar.addMenu("Settings")
        settings_action = settings_menu.addAction("Configure...")
        settings_action.triggered.connect(self.show_settings)

        # Create splitter
        splitter = QSplitter(Qt.Vertical)
        self.setCentralWidget(splitter)

        # Create top widget for chat history
        top_widget = QWidget()
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(0, 0, 0, 0)

        # Create a scroll area for messages
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setFrameStyle(QFrame.NoFrame)

        # Create container widget for messages
        self.messages_container = QWidget()
        self.messages_container.setStyleSheet("")
        self.messages_layout = QVBoxLayout(self.messages_container)
        self.messages_layout.setContentsMargins(20, 20, 20, 20)
        self.messages_layout.setSpacing(15)
        self.messages_layout.addStretch()

        self.scroll_area.setWidget(self.messages_container)
        top_layout.addWidget(self.scroll_area)
        splitter.addWidget(top_widget)

        # Create bottom widget for input and send button
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        bottom_layout.setSpacing(10)  # Add spacing between elements

        # Create chat input with expanding size policy
        self.chat_input = QTextEdit()
        self.chat_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create send button with fixed size policy
        send_button = QPushButton("Send")
        send_button.setMinimumWidth(80)  # Set minimum width
        send_button.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        send_button.clicked.connect(self.send_message)

        # Add widgets to layout
        bottom_layout.addWidget(self.chat_input)
        bottom_layout.addWidget(send_button, alignment=Qt.AlignVCenter)  # Align vertically
        bottom_layout.setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(bottom_widget)

        # Set initial sizes
        splitter.setSizes([400, 200])

    def initialize_chat_session(self):
        chroma = ChromaGateway()
        zk = Zettelkasten(
            tokenizer_gateway=TokenizerGateway(),
            vector_db=VectorDatabase(chroma_gateway=chroma, embeddings_gateway=EmbeddingsGateway()),
            filesystem_gateway=FilesystemGateway(self.config.vault))
        llm = LLMBroker(self.config.model)

        tools = [
            ResolveDateTool(),
            ReadZkDocument(zk),
            FindExcerptsRelatedTo(zk),
            FindZkDocumentsRelatedTo(zk),
        ]

        self.chat_session = ChatSession(
            llm,
            system_prompt="You are a helpful research assistant.",
            tools=tools
        )

    def show_settings(self):
        dialog = SettingsDialog(self.config, self)
        if dialog.exec():
            self.initialize_chat_session()

    def append_message(self, role: str, content: str = "", loading: bool = False) -> ChatMessageWidget:
        # Remove the stretch if it exists
        if self.messages_layout.count() > 0:
            stretch_item = self.messages_layout.itemAt(self.messages_layout.count() - 1)
            if stretch_item.spacerItem():
                self.messages_layout.removeItem(stretch_item)

        # Create and add the new message widget
        message_widget = ChatMessageWidget(role, content, loading)
        self.messages_layout.addWidget(message_widget)

        # Add stretch back at the bottom
        self.messages_layout.addStretch()

        # Scroll to the bottom to show the new message
        QTimer.singleShot(1, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))

        return message_widget

    @Slot()
    def send_message(self):
        message = self.chat_input.toPlainText().strip()
        if not message:
            return

        self.append_message("User", message)
        self.chat_input.clear()

        # Create assistant message with loading state
        assistant_widget = self.append_message("Assistant", loading=True)

        # Create and start worker thread for chat response
        self.worker = ChatWorker(self.chat_session, message)
        self.worker.response_ready.connect(lambda response: self.update_assistant_response(assistant_widget, response))
        self.worker.start()

    def update_assistant_response(self, widget: ChatMessageWidget, response: str):
        widget.set_loading(False)
        widget.set_content(response)
        # Ensure we scroll to see the complete response
        QTimer.singleShot(1, lambda: self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        ))


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
