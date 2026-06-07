"""
Bootstrap module for zk-chat.

Import this module before any chromadb imports to ensure
telemetry is disabled and logging is configured.
"""

import logging
import os

import structlog

# stdlib logging at WARN silences third-party libraries (chromadb, opentelemetry) that emit via stdlib logging
logging.basicConfig(level=logging.WARN)
# Route all structlog calls through stdlib logging so the level filter above applies
structlog.configure(
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
)
os.environ["CHROMA_TELEMETRY"] = "false"
