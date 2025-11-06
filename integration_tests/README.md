# Integration Tests Quick Start

## Overview

This directory contains end-to-end integration tests for zk-chat. Tests invoke the agent programmatically and validate results using "LLM as judge" approach.

## Structure

```
integration_tests/
├── conftest.py                  # Pytest configuration and fixtures
├── scenario_harness.py          # Core scenario execution framework
├── agent_runner.py              # Programmatic agent invocation
├── vault_builder.py             # Test vault construction
├── llm_validator.py             # LLM-as-judge validation
├── scenarios/                   # Scenario definitions
│   └── image_operations/
│       └── analyze_image_scenario.py
├── test_resources/              # Test images and files
│   └── README.md
└── image_operations_integration.py  # Test specs (use *_integration.py suffix)
```

## Prerequisites

1. In-repo module invocation: Tests call `python -m zk_chat.main` (no need to install the `zk-chat` package).
2. Test image: Place `zk-chat-architecture.png` in `integration_tests/test_resources/`.
3. Gateway configured: Tests auto-detect gateway based on environment

## Running Tests

### Quick Start (Auto-detect Gateway)

```bash
# Auto-detects OpenAI if OPENAI_API_KEY set, else uses Ollama
pytest integration_tests/ -v --spec
```

Note: The harness runs `python -m zk_chat.main query ...` to ensure the in-repo code is exercised.

### With Explicit Gateway

```bash
# Force Ollama
export ZK_TEST_GATEWAY=ollama
pytest integration_tests/ -v --spec

# Force OpenAI
export ZK_TEST_GATEWAY=openai
export OPENAI_API_KEY=your_key_here
pytest integration_tests/ -v --spec
```

### Run Specific Test

```bash
pytest integration_tests/image_operations_integration.py::DescribeImageAnalysis::should_analyze_architecture_diagram -v
```

## Gateway Configuration

Tests use smart defaults configured in `conftest.py`:

| Gateway | Text Model       | Visual Model             |
|---------|------------------|--------------------------|
| OpenAI  | gpt-4o           | gpt-4o                   |
| Ollama  | qwen3:8b         | gemma3:27b               |

Override via environment variables:

```bash
export ZK_TEST_GATEWAY=ollama              # or openai
export ZK_TEST_MODEL=my-text-model         # overrides text model
export ZK_TEST_VISUAL_MODEL=my-visual-model # overrides visual model
# For OpenAI:
export OPENAI_API_KEY=your_key_here
```

The test harness automatically passes both `--model` and `--visual-model` to the CLI when running tests, ensuring visual features are available for image analysis scenarios.

## What the Tests Do

1. **Create isolated vault** with test documents and images
2. **Execute agent** with natural language prompt
3. **Validate results** using LLM-as-judge (asks agent to verify work)
4. **Report pass/fail** with detailed reasoning

## Expected Test Duration

- **Ollama**: 2-5 minutes per test (depends on hardware)
- **OpenAI**: 1-3 minutes per test

## Troubleshooting

### Test skipped with "OPENAI_API_KEY not set"

If using OpenAI gateway explicitly, set API key:
```bash
export OPENAI_API_KEY=your_key_here
```

### Test fails with "Ollama is not running"

Start Ollama:
```bash
ollama serve
```

### Test fails with "Test resource image not found"

Place required image in `test_resources/`:
```bash
# Check what's needed
cat integration_tests/test_resources/README.md
```

### Test passes but validation seems wrong

Check detailed reasoning in test output:
```bash
pytest integration_tests/ -v -s  # -s shows all output
```

## Adding New Tests

1. **Create scenario** in `scenarios/` directory
2. **Create test file** with `*_integration.py` suffix
3. **Follow BDD style**: `class Describe*` and `def should_*`
4. **Use scenario_runner fixture**: Automatically configured

Example:
```python
class DescribeNewFeature:
    def should_do_something(self, scenario_runner, tmp_path):
        scenario = my_scenario()
        result = scenario_runner.run_scenario(scenario, tmp_path)
        assert result.passed
```

## Notes

- Tests are marked as `slow` automatically
- Image tests are marked `requires_visual`
- Use `-m "not slow"` to skip integration tests
- Each test creates isolated vault in temp directory
- Tests make real LLM calls (may incur costs with OpenAI)
