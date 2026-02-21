from typing import override

from zk_chat.config import Config
from zk_chat.config_gateway import ConfigGateway
from zk_chat.upgraders.gateway_specific_index_folder import Upgrader


class GatewaySpecificLastIndexed(Upgrader):
    """
    Upgrader to migrate from a single last_indexed field to gateway-specific last_indexed values.
    """

    def __init__(self, config: Config, config_gateway: ConfigGateway):
        self.config = config
        self.config_gateway = config_gateway

    @override
    def should_run(self) -> bool:
        # Run if we have a last_indexed value but no gateway-specific values
        return self.config.last_indexed is not None and not self.config.gateway_last_indexed

    @override
    def run(self):
        # Migrate the last_indexed value to the gateway-specific dictionary
        if self.config.last_indexed is not None:
            self.config.set_last_indexed(self.config.last_indexed)
            print(f"Migrated last_indexed value to gateway-specific storage for {self.config.gateway.value}")
            self.config_gateway.save(self.config)
