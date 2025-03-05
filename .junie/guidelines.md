# Project Guidelines

## Code Organization

### Import Structure
1. Imports should be grouped in the following order, with one blank line between groups:
   - Standard library imports
   - Third-party library imports
   - Local application imports
2. Within each group, imports should be sorted alphabetically

### Naming Conventions
1. Use descriptive variable names that indicate the purpose or content
2. Prefix test mock objects with 'mock_' (e.g., mock_memory)
3. Prefix test data variables with 'test_' (e.g., test_query)
4. Use '_' for unused variables or return values

### Type Hints and Documentation
1. Use type hints for method parameters and class dependencies
2. Include return type hints when the return type isn't obvious
3. Use docstrings for methods that aren't self-explanatory
4. Class docstrings should describe the purpose and behavior of the component

### Logging Conventions
1. Use structlog for all logging
2. Initialize logger at module level using `logger = structlog.get_logger()`
3. Include relevant context data in log messages
4. Use appropriate log levels:
   - INFO for normal operations
   - DEBUG for detailed information
   - WARNING for concerning but non-critical issues
   - ERROR for critical issues
5. Use print statements only for direct user feedback

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
10. Do not test private methods (starting with a _, eg _private_method) directly. Test them through the public API.

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
5. Organize test methods in a logical sequence:
   - Place instantiation/initialization tests first
   - Group related test scenarios together (e.g., success and failure cases)
6. Write assertions following these guidelines:
   - One assertion per line for better error identification
   - Use 'in' operator for partial string matches
   - Use '==' for exact matches
7. Use Mock's spec parameter to ensure type safety (e.g., `Mock(spec=SmartMemory)`)
8. Handle test data appropriately:
   - Use fixtures for reusable prerequisites
   - Define complex test data structures within test methods
   - Place module-level fixtures at the top of the file

#### Real Example

```python
class DescribeSmartMemory:
    def should_be_instantiated_with_chroma_gateway(self):
        mock_chroma_gateway = Mock(spec=ChromaGateway)

        memory = SmartMemory(mock_chroma_gateway)

        assert isinstance(memory, SmartMemory)
        assert memory.chroma == mock_chroma_gateway
```
