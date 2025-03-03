# Project Guidelines

## Testing Style Guide

### BDD-Style Tests

We follow a Behavior-Driven Development (BDD) style for our tests using the "Describe/should" pattern. This style makes
tests more readable and focuses on describing the behavior of our components.

#### Structure

1. Use pytest, do not use unittest
2. Test files should be named with a `_spec.py` suffix
3. The test file must be placed in the same folder as the file containing the test subject.
4. Tests are organized in classes that start with "Describe" followed by the name of the component being tested
5. Test methods start with "should_" and describe the expected behavior in plain English
6. Do not put comments above the Arrange / Act / Assert sections of the test, just put a blank line between them
7. Use pytest @fixture functions for initializing test prerequisites so that fixtures can be re-used.
    - Break up fixtures into smaller fixtures if they are too large
    - Put fixtures in module scope so that they could be shared between classes
8. Use pytest's `mocker` for mocking dependencies
9. Do not use conditional statements in tests. Each test should fail for only one clear reason.

#### Example

```python
class DescribeComponent:
    """
    Describe in plain language the purpose and behaviour of the component
    """

    def should_behave_in_specific_way(self):
# Set up your test prerequisites

# Execute the behavior you're testing

# Verify the expected outcomes
```

#### Best Practices

1. Use clear, descriptive names for test methods that explain the expected behavior
2. Follow the Arrange/Act/Assert pattern within test methods
3. Keep tests focused on a single behavior
4. Use meaningful assertions that verify the expected behavior

#### Real Example

```python
class DescribeSmartMemory:
    def should_be_instantiated_with_chroma_gateway(self):
        mock_chroma_gateway = Mock(spec=ChromaGateway)

        memory = SmartMemory(mock_chroma_gateway)

        assert isinstance(memory, SmartMemory)
        assert memory.chroma == mock_chroma_gateway
```