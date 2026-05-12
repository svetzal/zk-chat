"""
Integration tests for ConfigGateway.

These tests exercise real file I/O using a temporary directory — this is correct
for gateway tests, which should test the actual I/O behaviour rather than mocking it.
"""

import os
from unittest.mock import patch

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
def config_gateway():
    """Provide a ConfigGateway instance."""
    return ConfigGateway()


class DescribeConfigGateway:
    """Tests for ConfigGateway — vault config persistence."""

    def should_return_none_when_no_config_file_exists(self, config_gateway, tmp_vault):
        result = config_gateway.load(tmp_vault)

        assert result is None

    def should_load_config_from_existing_file(self, config_gateway, tmp_vault, sample_config):
        config_gateway.save(sample_config)

        result = config_gateway.load(tmp_vault)

        assert result is not None
        assert result.vault == tmp_vault
        assert result.model == "llama3.2"
        assert result.gateway == ModelGateway.OLLAMA

    def should_save_config_to_file(self, config_gateway, tmp_vault, sample_config):
        config_gateway.save(sample_config)

        config_path = os.path.join(tmp_vault, ".zk_chat")
        assert os.path.exists(config_path)

    def should_round_trip_config_through_save_and_load(self, config_gateway, tmp_vault):
        original = Config(
            vault=tmp_vault,
            model="mistral",
            gateway=ModelGateway.OPENAI,
            visual_model="gpt-4o",
            chunk_size=250,
            chunk_overlap=50,
        )

        config_gateway.save(original)
        loaded = config_gateway.load(tmp_vault)

        assert loaded is not None
        assert loaded.vault == original.vault
        assert loaded.model == original.model
        assert loaded.gateway == original.gateway
        assert loaded.visual_model == original.visual_model
        assert loaded.chunk_size == original.chunk_size
        assert loaded.chunk_overlap == original.chunk_overlap

    def should_overwrite_existing_config_on_save(self, config_gateway, tmp_vault, sample_config):
        config_gateway.save(sample_config)

        updated = Config(vault=tmp_vault, model="updated-model", gateway=ModelGateway.OLLAMA)
        config_gateway.save(updated)
        loaded = config_gateway.load(tmp_vault)

        assert loaded is not None
        assert loaded.model == "updated-model"

    def should_return_none_when_config_file_is_corrupt(self, config_gateway, tmp_vault):
        config_path = os.path.join(tmp_vault, ".zk_chat")
        with open(config_path, "w") as f:
            f.write("not valid json {{{")

        result = config_gateway.load(tmp_vault)

        assert result is None

    def should_return_none_when_config_file_has_wrong_types(self, config_gateway, tmp_vault):
        config_path = os.path.join(tmp_vault, ".zk_chat")
        with open(config_path, "w") as f:
            f.write('{"vault": 12345, "model": ["not", "a", "string"]}')

        result = config_gateway.load(tmp_vault)

        assert result is None

    def should_log_warning_when_config_file_is_corrupt(self, config_gateway, tmp_vault):
        config_path = os.path.join(tmp_vault, ".zk_chat")
        with open(config_path, "w") as f:
            f.write("not valid json {{{")

        with patch("zk_chat.config_gateway.logger") as mock_logger:
            config_gateway.load(tmp_vault)

        mock_logger.warning.assert_called_once()
        assert "Corrupt" in mock_logger.warning.call_args.args[0]
