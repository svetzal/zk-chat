import pytest
from pydantic import ValidationError

from zk_chat.init_options import InitOptions


class DescribeInitOptions:
    """Tests for the InitOptions model that captures the common_init contract."""

    def should_have_sensible_defaults(self):
        options = InitOptions()

        assert options.vault is None
        assert options.save is False
        assert options.gateway is None
        assert options.model is None
        assert options.visual_model is None
        assert options.reindex is True
        assert options.full is False
        assert options.unsafe is False
        assert options.git is False
        assert options.store_prompt is True
        assert options.reset_memory is False

    def should_be_frozen(self):
        options = InitOptions()

        with pytest.raises(ValidationError):
            options.vault = "/some/path"

    def should_accept_partial_construction(self):
        options = InitOptions(vault="/my/vault", full=True)

        assert options.vault == "/my/vault"
        assert options.full is True
        assert options.gateway is None
        assert options.reindex is True

    def should_accept_all_fields(self):
        options = InitOptions(
            vault="/vault",
            save=True,
            gateway="openai",
            model="gpt-4",
            visual_model="gpt-4o",
            reindex=False,
            full=True,
            unsafe=True,
            git=True,
            store_prompt=False,
            reset_memory=True,
        )

        assert options.vault == "/vault"
        assert options.save is True
        assert options.gateway == "openai"
        assert options.model == "gpt-4"
        assert options.visual_model == "gpt-4o"
        assert options.reindex is False
        assert options.full is True
        assert options.unsafe is True
        assert options.git is True
        assert options.store_prompt is False
        assert options.reset_memory is True
