"""
Service registry and provider system for zk-chat plugins.

This module provides a scalable way for plugins to request and access
the services they need without tight coupling to specific service implementations.
"""
from .document_service import DocumentService
from .index_service import IndexService
from .link_traversal_service import LinkTraversalService
from .plugin_base import ZkChatPlugin
from .service_provider import ServiceProvider
from .service_registry import ServiceRegistry, ServiceType

__all__ = [
    'ServiceRegistry',
    'ServiceType',
    'ServiceProvider',
    'ZkChatPlugin',
    'DocumentService',
    'IndexService',
    'LinkTraversalService',
]
