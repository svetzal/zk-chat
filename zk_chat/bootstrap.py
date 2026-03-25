"""
Bootstrap module for zk-chat.

Import this module before any chromadb imports to ensure
telemetry is disabled and logging is configured.
"""

import logging
import os

logging.basicConfig(level=logging.WARN)
os.environ["CHROMA_TELEMETRY"] = "false"
