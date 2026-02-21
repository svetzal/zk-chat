"""
Integration tests for ConfigGateway.

These tests exercise real file I/O using a temporary directory — this is correct
for gateway tests, which should test the actual I/O behaviour rather than mocking it.
"""

import os

import pytest

from zk_chat.config import Config, ModelGateway
from zk_chat.config_gateway import ConfigGateway


@pytest.fixture
def tmp_vault(tmp_path):
    """Provide a temporary vault directory."""
    return str(tmp_path)


@pytest.fixture
def sample_config(tmp_vault):
    """Provide a sample Config instance."""
    return Config(vault=tmp_vault, model="llama3.2", gateway=ModelGateway.OLLAMA)


@pytest.fixture
def gateway():
    """Provide a ConfigGateway instance."""
    return ConfigGateway()


class DescribeConfigGateway:
    """Tests for ConfigGateway — vault config persistence."""

    def should_return_none_when_no_config_file_exists(self, gateway, tmp_vault):
        result = gateway.load(tmp_vault)

        assert result is None

    def should_load_config_from_existing_file(self, gateway, tmp_vault, sample_config):
        gateway.save(sample_config)

        result = gateway.load(tmp_vault)

        assert result is not None
        assert result.vault == tmp_vault
        assert result.model == "llama3.2"
        assert result.gateway == ModelGateway.OLLAMA

    def should_save_config_to_file(self, gateway, tmp_vault, sample_config):
        gateway.save(sample_config)

        config_path = os.path.join(tmp_vault, ".zk_chat")
        assert os.path.exists(config_path)

    def should_round_trip_config_through_save_and_load(self, gateway, tmp_vault):
        original = Config(
            vault=tmp_vault,
            model="mistral",
            gateway=ModelGateway.OPENAI,
            visual_model="gpt-4o",
            chunk_size=250,
            chunk_overlap=50,
        )

        gateway.save(original)
        loaded = gateway.load(tmp_vault)

        assert loaded is not None
        assert loaded.vault == original.vault
        assert loaded.model == original.model
        assert loaded.gateway == original.gateway
        assert loaded.visual_model == original.visual_model
        assert loaded.chunk_size == original.chunk_size
        assert loaded.chunk_overlap == original.chunk_overlap

    def should_overwrite_existing_config_on_save(self, gateway, tmp_vault, sample_config):
        gateway.save(sample_config)

        updated = Config(vault=tmp_vault, model="updated-model", gateway=ModelGateway.OLLAMA)
        gateway.save(updated)
        loaded = gateway.load(tmp_vault)

        assert loaded is not None
        assert loaded.model == "updated-model"
