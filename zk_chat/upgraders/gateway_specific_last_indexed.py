import sys

if sys.version_info >= (3, 12):
    from typing import override
else:
    from typing_extensions import override

import structlog

from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.upgraders.gateway_specific_index_folder import Upgrader

logger = structlog.get_logger()


class GatewaySpecificLastIndexed(Upgrader):
    """
    Upgrader to migrate from a single last_indexed field to gateway-specific last_indexed values.
    """

    def __init__(self, config: Config, config_gateway: ConfigGateway) -> None:
        """Store the vault config and config gateway used to read and persist the migration."""
        self.config = config
        self.config_gateway = config_gateway

    @override
    def should_run(self) -> bool:
        """Return ``True`` when a legacy ``last_indexed`` value exists with no gateway-specific entries."""
        return self.config.last_indexed is not None and not self.config.gateway_last_indexed

    @override
    def run(self) -> None:
        """Copy ``last_indexed`` into the gateway-specific store and persist the updated config."""
        if self.config.last_indexed is not None:
            self.config.set_last_indexed(self.config.last_indexed)
            logger.info("Migrated last_indexed to gateway-specific storage", gateway=self.config.gateway.value)
            self.config_gateway.save(self.config)
