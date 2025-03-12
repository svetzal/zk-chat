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
5. Follow numpy docstring style

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

## Testing Guidelines

### General Rules
1. Use pytest for all testing
2. Test files:
   - Named with `_spec.py` suffix
   - Co-located with implementation files (same folder as the test subject)
3. Code style:
   - Max line length: 127
   - Max complexity: 10
4. Run tests with: `pytest`
5. Run linting with: `flake8 src`

### BDD-Style Tests
We follow a Behavior-Driven Development (BDD) style using the "Describe/should" pattern to make tests readable and focused on component behavior.

#### Test Structure
1. Tests are organized in classes that start with "Describe" followed by the component name
2. Test methods:
   - Start with "should_"
   - Describe the expected behavior in plain English
   - Follow the Arrange/Act/Assert pattern (separated by blank lines)
3. No conditional statements in tests - each test should fail for only one clear reason
4. Do not test private methods directly (those starting with '_') - test through the public API

#### Fixtures and Mocking
1. Use pytest @fixture for test prerequisites:
   - Break large fixtures into smaller, reusable ones
   - Place fixtures in module scope for sharing between classes
   - Place module-level fixtures at the top of the file
2. Mocking:
   - Use pytest's `mocker` for dependencies
   - Use Mock's spec parameter for type safety (e.g., `Mock(spec=SmartMemory)`)
   - Only mock our own gateway classes
   - Do not mock library internals or private functions
   - Do not use unittest or MagicMock directly

#### Best Practices
1. Test organization:
   - Place instantiation/initialization tests first
   - Group related scenarios together (success and failure cases)
   - Keep tests focused on single behaviors
2. Assertions:
   - One assertion per line for better error identification
   - Use 'in' operator for partial string matches
   - Use '==' for exact matches
3. Test data:
   - Use fixtures for reusable prerequisites
   - Define complex test data structures within test methods

### Example

```python
class DescribeSmartMemory:
    """
    Tests for the SmartMemory component which handles memory operations
    """
    def should_be_instantiated_with_chroma_gateway(self):
        mock_chroma_gateway = Mock(spec=ChromaGateway)

        memory = SmartMemory(mock_chroma_gateway)

        assert isinstance(memory, SmartMemory)
        assert memory.chroma == mock_chroma_gateway
```
