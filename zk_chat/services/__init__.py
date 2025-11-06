"""
Service registry and provider system for zk-chat plugins.

This module provides a scalable way for plugins to request and access
the services they need without tight coupling to specific service implementations.
"""
from .plugin_base import ZkChatPlugin
from .service_provider import ServiceProvider
from .service_registry import ServiceRegistry, ServiceType

__all__ = ['ServiceRegistry', 'ServiceType', 'ServiceProvider', 'ZkChatPlugin']
