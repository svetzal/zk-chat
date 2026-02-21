"""
Unit tests for the pure Config data model.

Config should be a plain Pydantic model with no file I/O — all persistence
lives in ConfigGateway. These tests verify the pure data behaviour.
"""

from datetime import datetime

from zk_chat.config import Config, ModelGateway


class DescribeConfig:
    """Tests for the pure Config data model."""

    def should_instantiate_with_required_fields(self):
        config = Config(vault="/some/vault", model="llama3.2")

        assert config.vault == "/some/vault"
        assert config.model == "llama3.2"

    def should_default_gateway_to_ollama(self):
        config = Config(vault="/some/vault", model="llama3.2")

        assert config.gateway == ModelGateway.OLLAMA

    def should_default_visual_model_to_none(self):
        config = Config(vault="/some/vault", model="llama3.2")

        assert config.visual_model is None

    def should_default_chunk_size_to_500(self):
        config = Config(vault="/some/vault", model="llama3.2")

        assert config.chunk_size == 500

    def should_default_chunk_overlap_to_100(self):
        config = Config(vault="/some/vault", model="llama3.2")

        assert config.chunk_overlap == 100

    class DescribeGetLastIndexed:
        """Tests for get_last_indexed() pure method."""

        def should_return_none_when_no_last_indexed(self):
            config = Config(vault="/some/vault", model="llama3.2")

            result = config.get_last_indexed()

            assert result is None

        def should_get_last_indexed_for_current_gateway(self):
            config = Config(vault="/some/vault", model="llama3.2", gateway=ModelGateway.OLLAMA)
            timestamp = datetime(2025, 1, 15, 10, 30)
            config.gateway_last_indexed["ollama"] = timestamp

            result = config.get_last_indexed()

            assert result == timestamp

        def should_fall_back_to_deprecated_last_indexed_field(self):
            old_timestamp = datetime(2024, 6, 1, 8, 0)
            config = Config(vault="/some/vault", model="llama3.2", last_indexed=old_timestamp)

            result = config.get_last_indexed()

            assert result == old_timestamp

        def should_prefer_gateway_specific_over_deprecated_field(self):
            old_timestamp = datetime(2024, 6, 1, 8, 0)
            new_timestamp = datetime(2025, 1, 15, 10, 30)
            config = Config(vault="/some/vault", model="llama3.2", last_indexed=old_timestamp)
            config.gateway_last_indexed["ollama"] = new_timestamp

            result = config.get_last_indexed()

            assert result == new_timestamp

        def should_get_last_indexed_for_specified_gateway(self):
            config = Config(vault="/some/vault", model="llama3.2", gateway=ModelGateway.OLLAMA)
            ollama_ts = datetime(2025, 1, 10)
            openai_ts = datetime(2025, 1, 15)
            config.gateway_last_indexed["ollama"] = ollama_ts
            config.gateway_last_indexed["openai"] = openai_ts

            result = config.get_last_indexed(ModelGateway.OPENAI)

            assert result == openai_ts

    class DescribeSetLastIndexed:
        """Tests for set_last_indexed() pure method."""

        def should_set_last_indexed_for_current_gateway(self):
            config = Config(vault="/some/vault", model="llama3.2", gateway=ModelGateway.OLLAMA)
            timestamp = datetime(2025, 1, 15, 10, 30)

            config.set_last_indexed(timestamp)

            assert config.gateway_last_indexed["ollama"] == timestamp

        def should_set_last_indexed_for_specified_gateway(self):
            config = Config(vault="/some/vault", model="llama3.2", gateway=ModelGateway.OLLAMA)
            timestamp = datetime(2025, 1, 15, 10, 30)

            config.set_last_indexed(timestamp, ModelGateway.OPENAI)

            assert config.gateway_last_indexed["openai"] == timestamp

        def should_overwrite_existing_gateway_last_indexed(self):
            config = Config(vault="/some/vault", model="llama3.2")
            first = datetime(2025, 1, 1)
            second = datetime(2025, 1, 15)
            config.set_last_indexed(first)
            config.set_last_indexed(second)

            assert config.gateway_last_indexed["ollama"] == second
