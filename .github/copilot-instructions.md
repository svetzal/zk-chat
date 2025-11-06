# Project Guidelines

## Code Organization

### Program Entry Points
1. All code is located in the `zk_chat` folder
2. The UI is launched by running `zk_chat/qt.py`
3. The CLI tool is launched by running `zk_chat/cli.py`

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

### Code Conventions
1. Do not write comments that just restate what the code does
2. Use pydantic BaseModel classes, do not use @dataclass

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
3. Do not use comments (eg Arrange, Act, Assert) to delineate test sections - just use a blank line
4. No conditional statements in tests - each test should fail for only one clear reason
5. Do not test private methods directly (those starting with '_') - test through the public API

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

## Release Process

This project follows [Semantic Versioning](https://semver.org/) (SemVer) for version numbering. The version format is MAJOR.MINOR.PATCH, where:

1. MAJOR version increases for incompatible API changes
2. MINOR version increases for backward-compatible functionality additions
3. PATCH version increases for backward-compatible bug fixes

### Release Checklist

Follow these steps in order when preparing and publishing a release:

1. **Verification Phase**:
   ```bash
   # All lint checks must pass
   ruff check zk_chat

   # All unit tests must pass
   pytest zk_chat/

   # All integration tests must pass
   pytest integration_tests/
   ```

2. **Documentation Phase**:
   - Ensure CHANGELOG.md is up to date with all changes for this release
   - Move items from "[Next]" section to new version section: `## [X.Y.Z] - YYYY-MM-DD`
   - Verify README.md reflects current features and version
   - Ensure all documentation in docs/ is current
   - Update version in pyproject.toml

3. **Commit and Push**:
   ```bash
   # Commit release changes
   git add pyproject.toml CHANGELOG.md README.md docs/
   git commit -m "Release vX.Y.Z with [brief description]"

   # Push to trigger CI/CD validation
   git push
   ```

4. **Monitor Build**:
   ```bash
   # Monitor the GitHub Actions workflow
   gh run watch

   # Wait for green build before proceeding
   # If build fails, fix issues and repeat from step 1
   ```

5. **Tag Release**:
   ```bash
   # Create tag in format RELEASE_MAJOR_MINOR_PATCH
   # Example: for version 3.5.0, tag is RELEASE_3_5_0
   git tag RELEASE_X_Y_Z

   # Push the tag to trigger release workflow
   git push origin RELEASE_X_Y_Z
   ```

6. **Monitor Release Build**:
   ```bash
   # Watch the release workflow
   gh run watch

   # Verify:
   # - Documentation deployed to GitHub Pages
   # - Package published to PyPI
   ```

7. **Create GitHub Release**:
   ```bash
   # Create release with content from CHANGELOG
   gh release create RELEASE_X_Y_Z \
     --title "vX.Y.Z - [Brief Title]" \
     --notes "$(sed -n '/## \[X.Y.Z\]/,/## \[/p' CHANGELOG.md | head -n -1)"

   # Or create interactively to edit release notes
   gh release create RELEASE_X_Y_Z --draft --generate-notes
   ```

### Release Types

#### Major Releases (X.0.0)

Major releases may include:
- Breaking API changes (eg tool plugin interfacing)
- Significant architectural changes
- Removal of deprecated features
- Changes that require users to modify their code or workflow

For major releases, consider:
- Providing migration guides
- Updating all documentation thoroughly
- Highlighting breaking changes prominently in the CHANGELOG

#### Minor Releases (0.X.0)

Minor releases may include:
- New features
- Non-breaking enhancements
- Deprecation notices (but not removal of deprecated features)
- Performance improvements

For minor releases:
- Document all new features
- Update README to highlight new capabilities
- Ensure backward compatibility

#### Patch Releases (0.0.X)

Patch releases should be limited to:
- Bug fixes
- Security updates
- Performance improvements that don't change behavior
- Documentation corrections

For patch releases:
- Clearly describe the issues fixed
- Avoid introducing new features
- Maintain strict backward compatibility
