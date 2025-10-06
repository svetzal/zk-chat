"""
Pytest configuration for integration tests.

Provides fixtures and configuration for integration test execution.
"""
import os
import pytest
from pathlib import Path

from integration_tests.scenario_harness import ScenarioRunner

DEFAULT_MODELS = {
    "openai": {
        "text": "gpt-4o",
        "visual": "gpt-4o"
    },
    "ollama": {
        "text": "qwen2.5:32b",
        "visual": "llama3.2-vision:11b"
    }
}


def _determine_gateway():
    """
    Determine which gateway to use with smart defaults.

    Priority:
    1. ZK_TEST_GATEWAY environment variable if set
    2. OpenAI if OPENAI_API_KEY is set
    3. Ollama as fallback
    """
    explicit_gateway = os.environ.get("ZK_TEST_GATEWAY")
    if explicit_gateway:
        if explicit_gateway not in ["ollama", "openai"]:
            raise ValueError(f"Invalid ZK_TEST_GATEWAY: {explicit_gateway}. Must be 'ollama' or 'openai'.")
        return explicit_gateway

    if os.environ.get("OPENAI_API_KEY"):
        return "openai"

    return "ollama"


def _get_models(gateway):
    """Get text and visual models for the gateway"""
    text_model = os.environ.get("ZK_TEST_MODEL")
    visual_model = os.environ.get("ZK_TEST_VISUAL_MODEL")

    if not text_model:
        text_model = DEFAULT_MODELS[gateway]["text"]

    if not visual_model:
        visual_model = DEFAULT_MODELS[gateway]["visual"]

    return text_model, visual_model


@pytest.fixture(scope="session")
def test_resources_dir():
    """Path to test resource files"""
    return Path(__file__).parent / "test_resources"


@pytest.fixture(scope="session")
def gateway_config():
    """Determine and validate gateway configuration"""
    gateway = _determine_gateway()
    text_model, visual_model = _get_models(gateway)

    if gateway == "openai" and not os.environ.get("OPENAI_API_KEY"):
        pytest.skip(
            "OPENAI_API_KEY environment variable not set. "
            "Required when using OpenAI gateway."
        )

    return {
        "gateway": gateway,
        "text_model": text_model,
        "visual_model": visual_model
    }


@pytest.fixture
def scenario_runner(gateway_config):
    """Create a scenario runner for tests"""
    return ScenarioRunner(
        gateway=gateway_config["gateway"],
        model=gateway_config["text_model"],
        visual_model=gateway_config["visual_model"]
    )


def pytest_configure(config):
    """Configure pytest for integration tests"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "requires_visual: marks tests requiring visual model"
    )


def pytest_collection_modifyitems(config, items):
    """Add markers to integration tests"""
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

        if "image" in item.name.lower() or "visual" in item.name.lower():
            item.add_marker(pytest.mark.requires_visual)
