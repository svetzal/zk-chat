from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                              QTextEdit, QPushButton, QMenuBar, QMenu, QDialog,
                              QLabel, QLineEdit, QComboBox, QFileDialog, QMessageBox,
                              QSplitter, QHBoxLayout, QSizePolicy)
from PySide6.QtCore import Qt, Signal, Slot, QThread
import sys
import os
from typing import Optional

from zk_chat.config import Config, get_available_models
from zk_chat.chat import ChatSession, LLMBroker, ChromaGateway, Zettelkasten
from zk_chat.vector_database import VectorDatabase
from mojentic.llm.gateways.embeddings_gateway import EmbeddingsGateway
from mojentic.llm.gateways.tokenizer_gateway import TokenizerGateway
from mojentic.llm.tools.date_resolver import ResolveDateTool
from zk_chat.tools.find_excerpts_related_to import FindExcerptsRelatedTo
from zk_chat.tools.find_zk_documents_related_to import FindZkDocumentsRelatedTo
from zk_chat.tools.read_zk_document import ReadZkDocument
from zk_chat.tools.write_zk_document import WriteZkDocument


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
        self.chat_history = QTextEdit()
        self.chat_history.setReadOnly(True)
        top_layout.addWidget(self.chat_history)
        top_layout.setContentsMargins(0, 0, 0, 0)
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
            root_path=self.config.vault,
            tokenizer_gateway=TokenizerGateway(),
            vector_db=VectorDatabase(chroma_gateway=chroma, embeddings_gateway=EmbeddingsGateway())
        )
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

    def append_message(self, role: str, content: str):
        self.chat_history.append(f"<b>{role}:</b> {content}")

    @Slot()
    def send_message(self):
        message = self.chat_input.toPlainText().strip()
        if not message:
            return

        self.append_message("User", message)
        self.chat_input.clear()

        # Create and start worker thread for chat response
        self.worker = ChatWorker(self.chat_session, message)
        self.worker.response_ready.connect(lambda response: self.append_message("Assistant", response))
        self.worker.start()


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
