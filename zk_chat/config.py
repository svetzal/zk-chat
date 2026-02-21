from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class ModelGateway(StrEnum):
    OLLAMA = "ollama"
    OPENAI = "openai"


class Config(BaseModel):
    vault: str
    model: str  # Chat model
    visual_model: str | None = None  # Visual analysis model
    gateway: ModelGateway = ModelGateway.OLLAMA
    chunk_size: int = 500
    chunk_overlap: int = 100
    last_indexed: datetime | None = None  # Deprecated, kept for backward compatibility
    gateway_last_indexed: dict[str, datetime] = Field(default_factory=dict)

    def get_last_indexed(self, gateway: ModelGateway | None = None) -> datetime | None:
        """
        Get the last indexed time for the specified gateway or the current gateway if not specified.
        Falls back to the deprecated last_indexed field if the gateway-specific value is not found.
        """
        gateway_value = gateway.value if gateway else self.gateway.value
        if gateway_value in self.gateway_last_indexed:
            return self.gateway_last_indexed[gateway_value]
        return self.last_indexed

    def set_last_indexed(self, timestamp: datetime, gateway: ModelGateway | None = None):
        """
        Set the last indexed time for the specified gateway or the current gateway if not specified.
        """
        gateway_value = gateway.value if gateway else self.gateway.value
        self.gateway_last_indexed[gateway_value] = timestamp
