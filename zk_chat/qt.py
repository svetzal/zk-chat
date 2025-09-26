import os
import sys

# Disable ChromaDB telemetry to avoid PostHog compatibility issues
os.environ['CHROMA_TELEMETRY'] = 'false'

from PySide6.QtCore import Qt, Signal, Slot, QThread, QTimer
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                               QTextEdit, QPushButton, QDialog, QFrame,
                               QLabel, QLineEdit, QComboBox, QFileDialog, QSplitter, QHBoxLayout, QSizePolicy,
                               QTextBrowser, QScrollArea, QProgressBar)
from mojentic.llm.gateways import OllamaGateway, OpenAIGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
from mojentic.llm.tools.date_resolver import ResolveDateTool

from zk_chat.chat import ChatSession, LLMBroker, ChromaGateway, Zettelkasten
from zk_chat.chroma_collections import ZkCollectionName
from zk_chat.config import Config, get_available_models, ModelGateway
from zk_chat.filesystem_gateway import MarkdownFilesystemGateway
from zk_chat.tools.analyze_image import AnalyzeImage
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.resolve_wikilink import ResolveWikiLink
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

        # Gateway selection
        gateway_layout = QVBoxLayout()
        gateway_label = QLabel("Model Gateway:")
        self.gateway_combo = QComboBox()
        self.gateway_combo.addItems([gateway.value for gateway in ModelGateway])
        current_gateway_index = self.gateway_combo.findText(self.config.gateway.value)
        if current_gateway_index >= 0:
            self.gateway_combo.setCurrentIndex(current_gateway_index)
        self.gateway_combo.currentIndexChanged.connect(self.update_model_list)
        gateway_layout.addWidget(gateway_label)
        gateway_layout.addWidget(self.gateway_combo)
        layout.addLayout(gateway_layout)

        # Chat Model selection
        chat_model_layout = QVBoxLayout()
        chat_model_label = QLabel("Chat Model:")
        self.chat_model_combo = QComboBox()
        chat_model_layout.addWidget(chat_model_label)
        chat_model_layout.addWidget(self.chat_model_combo)
        layout.addLayout(chat_model_layout)

        # Visual Model selection
        visual_model_layout = QVBoxLayout()
        visual_model_label = QLabel("Visual Analysis Model (optional):")
        self.visual_model_combo = QComboBox()
        # Add a "None" option to disable visual analysis
        self.visual_model_combo.addItem("None - Disable Visual Analysis")
        visual_model_layout.addWidget(visual_model_label)
        visual_model_layout.addWidget(self.visual_model_combo)
        layout.addLayout(visual_model_layout)

        # Populate model lists based on selected gateway
        self.update_model_list()

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Zettelkasten Folder")
        if folder:
            self.folder_edit.setText(folder)

    def update_model_list(self):
        # Get the selected gateway
        gateway_text = self.gateway_combo.currentText()
        gateway = ModelGateway(gateway_text)

        # Check if OpenAI gateway is selected and OPENAI_API_KEY is not set
        if gateway == ModelGateway.OPENAI and not os.environ.get("OPENAI_API_KEY"):
            # Show a warning message
            self.chat_model_combo.clear()
            self.chat_model_combo.addItem("OPENAI_API_KEY environment variable is not set")
            self.visual_model_combo.clear()
            self.visual_model_combo.addItem("OPENAI_API_KEY environment variable is not set")
            return

        # Get available models for the selected gateway
        available_models = get_available_models(gateway)

        # Update the chat model combo box
        self.chat_model_combo.clear()
        self.chat_model_combo.addItems(available_models)

        # Try to select the current chat model if it's available
        current_chat_index = self.chat_model_combo.findText(self.config.model)
        if current_chat_index >= 0:
            self.chat_model_combo.setCurrentIndex(current_chat_index)
        elif self.chat_model_combo.count() > 0:
            # Otherwise select the first model
            self.chat_model_combo.setCurrentIndex(0)

        # Update the visual model combo box
        self.visual_model_combo.clear()
        # Add the "None" option first
        self.visual_model_combo.addItem("None - Disable Visual Analysis")
        self.visual_model_combo.addItems(available_models)

        # Try to select the current visual model if it's available
        if self.config.visual_model:
            current_visual_index = self.visual_model_combo.findText(self.config.visual_model)
            if current_visual_index >= 0:
                self.visual_model_combo.setCurrentIndex(current_visual_index)
            else:
                # If the current model isn't available, select the first model (after "None")
                self.visual_model_combo.setCurrentIndex(1)
        else:
            # If no visual model is set, select "None"
            self.visual_model_combo.setCurrentIndex(0)

    def save_settings(self):
        self.config.vault = self.folder_edit.text()
        self.config.gateway = ModelGateway(self.gateway_combo.currentText())
        self.config.model = self.chat_model_combo.currentText()

        # Set visual_model to None if "None - Disable Visual Analysis" is selected
        selected_visual_model = self.visual_model_combo.currentText()
        if selected_visual_model == "None - Disable Visual Analysis":
            self.config.visual_model = None
        else:
            self.config.visual_model = selected_visual_model

        self.config.save()
        self.accept()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # TODO: This is a placeholder. In a real application, we would need to get the vault path from somewhere.
        vault_path = os.path.expanduser("~/Documents")
        self.config = Config.load_or_initialize(vault_path)
        self.chat_session = None
        self.initialize_chat_session()

        self.setWindowTitle("Zk-Chat")
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
        db_dir = os.path.join(self.config.vault, ".zk_chat_db")
        chroma = ChromaGateway(self.config.gateway, db_dir=db_dir)

        # Create the appropriate gateway based on configuration
        if self.config.gateway == ModelGateway.OLLAMA:
            gateway = OllamaGateway()
        elif self.config.gateway == ModelGateway.OPENAI:
            gateway = OpenAIGateway(os.environ.get("OPENAI_API_KEY"))
        else:
            # Default to Ollama if not specified
            gateway = OllamaGateway()

        zk = Zettelkasten(
            tokenizer_gateway=TokenizerGateway(),
            excerpts_db=VectorDatabase(
                chroma_gateway=chroma,
                gateway=gateway,
                collection_name=ZkCollectionName.EXCERPTS
            ),
            documents_db=VectorDatabase(
                chroma_gateway=chroma,
                gateway=gateway,
                collection_name=ZkCollectionName.DOCUMENTS
            ),
            filesystem_gateway=MarkdownFilesystemGateway(self.config.vault))
        # Create LLM broker for chat
        chat_llm = LLMBroker(self.config.model, gateway=self.config.gateway.value)

        # Initialize tools list with basic tools
        tools = [
            ResolveDateTool(),
            ReadZkDocument(zk),
            FindExcerptsRelatedTo(zk),
            FindZkDocumentsRelatedTo(zk),
            ResolveWikiLink(zk.filesystem_gateway),
        ]

        # Add AnalyzeImage tool only if a visual model is selected
        if self.config.visual_model:
            visual_llm = LLMBroker(self.config.visual_model, gateway=self.config.gateway.value)
            tools.append(AnalyzeImage(zk, visual_llm))

        self.chat_session = ChatSession(
            chat_llm,
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
