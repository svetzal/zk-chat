# Integration Testing Plan

## Overview

This document outlines the plan for implementing comprehensive integration tests for the zk-chat project. These tests will be executed prior to each public release to ensure the system works correctly end-to-end across increasingly sophisticated use cases.

## Goals

1. **Validate Real-World Workflows**: Test actual user scenarios from start to finish
2. **Pre-Release Validation**: Provide confidence before public releases
3. **Regression Prevention**: Catch breaking changes in complex interactions
4. **Documentation via Tests**: Demonstrate expected behavior through executable examples

## Testing Philosophy

### Integration vs Unit Tests

- **Unit tests** (`*_spec.py`): Test individual components in isolation with mocks
- **Integration tests** (`*_integration_spec.py`): Test complete end-to-end workflows by invoking the agent programmatically
- **Location**: Integration tests will be in a dedicated `zk_chat/integration/` directory

### Test Data Strategy

- Each test scenario creates its own isolated test vault with scenario-specific content
- Tests invoke the agent programmatically with natural language prompts
- Use real LLM calls to exercise actual behavior
- Validation uses "LLM as judge" - a second agent prompt verifies the work was done correctly
- Tests are declarative: define scenario setup, execution prompt, and validation criteria

### LLM as Judge Approach

Rather than asserting exact outputs, we use a two-phase approach:

1. **Execution Phase**: Agent receives a prompt to perform work (e.g., "Create a Map of Content about Python")
2. **Validation Phase**: A separate validation prompt asks the agent to check if the work meets criteria:
   - "Examine the vault and verify that a Map of Content about Python was created"
   - "Check that it includes wikilinks to relevant documents"
   - "Verify the structure follows MoC conventions"
   - Agent responds with pass/fail and reasoning

This approach allows for subjective quality validation while remaining maintainable.

## Test Architecture

### Directory Structure

**Important**: Integration tests are in a separate `integration_tests/` directory (not under `zk_chat/`) and use `_integration.py` suffix (not `_spec.py`) to clearly distinguish them from unit tests.

```
integration_tests/                          # Separate from unit tests
  __init__.py
  conftest.py                               # Pytest configuration

  # Core infrastructure
  scenario_harness.py                       # Scenario execution framework
  agent_runner.py                           # Programmatic agent invocation
  vault_builder.py                          # Declarative vault construction
  llm_validator.py                          # LLM as judge validation

  # Test resources
  test_resources/
    test_architecture_diagram.png
    test_whiteboard_features.jpg
    test_whiteboard_priorities.jpg
    test_code_screenshot.png
    test_presentation_slide.png

  # Scenario definitions
  scenarios/
    __init__.py
    basic_operations/
      __init__.py
      create_document_scenario.py
      read_document_scenario.py
      update_document_scenario.py
      rename_document_scenario.py
    rag_operations/
      __init__.py
      query_documents_scenario.py
      summarize_topic_scenario.py
    moc_generation/
      __init__.py
      generate_moc_scenario.py
      update_moc_scenario.py
    image_operations/
      __init__.py
      generate_caption_scenario.py
      analyze_screenshot_scenario.py
      analyze_whiteboard_scenario.py

  # Test files that run scenarios (use _integration.py suffix)
  basic_operations_integration.py
  rag_operations_integration.py
  moc_generation_integration.py
  image_operations_integration.py
```

### Naming Conventions

- **Directory**: `integration_tests/` (top-level, not under `zk_chat/`)
- **Test files**: Use `*_integration.py` suffix (not `_spec.py`)
- **Test classes**: Still use `Describe*` pattern for consistency
- **Test methods**: Still use `should_*` pattern for consistency
- **Discovery**: Pytest finds `*_integration.py` files via configuration

### Core Infrastructure Components

#### 1. Scenario Harness (`scenario_harness.py`)

The harness provides a declarative way to define test scenarios using Pydantic models for strong typing:

```python
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Callable, Any

class Document(BaseModel):
    """Represents a document to be created in test vault"""
    path: str
    content: str
    metadata: Optional[Dict[str, Any]] = None

class ImageFile(BaseModel):
    """Represents an image file to be placed in test vault"""
    path: str
    source_path: str  # Path to actual test image file

class ValidationCriterion(BaseModel):
    """A single validation criterion"""
    description: str
    prompt: str
    success_keywords: Optional[List[str]] = None

class IntegrationScenario(BaseModel):
    """Complete specification of an integration test scenario"""
    name: str
    description: str

    # Setup
    initial_documents: List[Document]
    initial_images: Optional[List[ImageFile]] = None

    # Execution
    execution_prompt: str
    agent_mode: str = "interactive"  # or "autonomous"
    unsafe: bool = False
    use_git: bool = False

    # Validation
    validation_criteria: Optional[List[ValidationCriterion]] = None

    # Optional custom validation (excluded from serialization)
    custom_validation: Optional[Callable] = Field(default=None, exclude=True)

class ScenarioRunner:
    """Executes integration scenarios"""

    def __init__(self, gateway: str, model: str, visual_model: str = None):
        self.gateway = gateway
        self.model = model
        self.visual_model = visual_model

    def run_scenario(self, scenario: IntegrationScenario, tmp_path: Path) -> ScenarioResult:
        """
        Execute a complete integration scenario.

        Returns ScenarioResult with pass/fail and details.
        """
        # 1. Build vault
        vault_path = self._build_vault(scenario, tmp_path)

        # 2. Execute agent with prompt
        execution_result = self._execute_agent(scenario, vault_path)

        # 3. Validate using LLM as judge
        validation_result = self._validate_scenario(scenario, vault_path, execution_result)

        # 4. Run custom validation if provided
        if scenario.custom_validation:
            custom_result = scenario.custom_validation(vault_path, execution_result)
            validation_result = validation_result.merge(custom_result)

        return validation_result

    def _build_vault(self, scenario: IntegrationScenario, tmp_path: Path) -> Path:
        """Build isolated test vault for scenario"""
        vault_builder = VaultBuilder(tmp_path)
        return vault_builder.build(scenario.initial_documents, scenario.initial_images)

    def _execute_agent(self, scenario: IntegrationScenario, vault_path: Path) -> ExecutionResult:
        """Execute agent with scenario prompt"""
        runner = AgentRunner(
            vault_path=vault_path,
            gateway=self.gateway,
            model=self.model,
            agent_mode=scenario.agent_mode,
            unsafe=scenario.unsafe,
            use_git=scenario.use_git
        )
        return runner.run(scenario.execution_prompt)

    def _validate_scenario(
        self,
        scenario: IntegrationScenario,
        vault_path: Path,
        execution_result: ExecutionResult
    ) -> ValidationResult:
        """Validate scenario using LLM as judge"""
        validator = LLMValidator(
            vault_path=vault_path,
            gateway=self.gateway,
            model=self.model
        )
        return validator.validate(scenario.validation_criteria)

class ExecutionResult(BaseModel):
    """Result of agent execution"""
    success: bool
    output: str
    error: Optional[str] = None
    duration: float = 0.0

class ValidationResult(BaseModel):
    """Result of validation"""
    passed: bool
    criteria_results: List[Dict[str, Any]]
    overall_reasoning: str

    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge with another validation result"""
        return ValidationResult(
            passed=self.passed and other.passed,
            criteria_results=self.criteria_results + other.criteria_results,
            overall_reasoning=f"{self.overall_reasoning}\n\n{other.overall_reasoning}"
        )

class ScenarioResult(BaseModel):
    """Complete result of scenario execution and validation"""
    scenario_name: str
    execution_result: ExecutionResult
    validation_result: ValidationResult

    @property
    def passed(self) -> bool:
        return self.execution_result.success and self.validation_result.passed
```

**Note on Model Usage:** The integration test `Document` class is distinct from `ZkDocument` in `zk_chat/models.py`:

- **`Document` (integration tests)**: A simple test fixture model for declaratively defining test scenario setup. Uses `path` (the file path where the document will be created), `content`, and `metadata`.
  
- **`ZkDocument` (zk_chat/models.py)**: The production model representing actual Zettelkasten documents. Uses `relative_path` (within the vault), `metadata`, and `content`, with additional methods for computing `title` and `id`.

Both use Pydantic `BaseModel` following the project's coding guidelines. The integration test `Document` is intentionally simpler as it only needs to specify test data, while `ZkDocument` includes business logic for document handling.

#### 2. Agent Runner (`agent_runner.py`)

Handles programmatic invocation of the agent:

```python
import subprocess
from pathlib import Path
from typing import Optional

class AgentRunner:
    """Runs the zk-chat agent programmatically"""

    def __init__(
        self,
        vault_path: Path,
        gateway: str,
        model: Optional[str] = None,
        visual_model: Optional[str] = None,
        agent_mode: str = "interactive",
        unsafe: bool = False,
        use_git: bool = False
    ):
        self.vault_path = vault_path
        self.gateway = gateway
        self.model = model
        self.visual_model = visual_model
        self.agent_mode = agent_mode
        self.unsafe = unsafe
        self.use_git = use_git

    def run(self, prompt: str, timeout: int = 300) -> ExecutionResult:
        """
        Execute agent with given prompt.

        Uses subprocess to invoke zk-chat CLI with the prompt.
        Returns ExecutionResult with output and timing.
        """
        import time

        start_time = time.time()

        # Build command
        cmd = [
            "zk-chat", "query",
            "--vault", str(self.vault_path),
            "--gateway", self.gateway
        ]

        if self.model:
            cmd.extend(["--model", self.model])

        if self.agent_mode == "autonomous":
            cmd.append("--agent")

        if self.unsafe:
            cmd.append("--unsafe")

        if self.use_git:
            cmd.append("--git")

        cmd.append(prompt)

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout
            )

            duration = time.time() - start_time

            return ExecutionResult(
                success=(result.returncode == 0),
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None,
                duration=duration
            )

        except subprocess.TimeoutExpired:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=f"Agent execution timed out after {timeout} seconds",
                duration=duration
            )

        except Exception as e:
            duration = time.time() - start_time
            return ExecutionResult(
                success=False,
                output="",
                error=str(e),
                duration=duration
            )
```

#### 3. Vault Builder (`vault_builder.py`)

Constructs test vaults from scenario specifications:

```python
from pathlib import Path
from typing import List, Optional
import shutil

class VaultBuilder:
    """Builds test vaults from scenario specifications"""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.vault_path = base_path / "test_vault"

    def build(
        self,
        documents: List[Document],
        images: Optional[List[ImageFile]] = None
    ) -> Path:
        """
        Build a test vault with specified documents and images.

        Returns path to created vault.
        """
        # Create vault directory
        self.vault_path.mkdir(parents=True, exist_ok=True)

        # Create documents
        for doc in documents:
            self._create_document(doc)

        # Copy images if provided
        if images:
            for img in images:
                self._copy_image(img)

        # Initialize vault (this will create .zk_chat config)
        self._initialize_vault()

        return self.vault_path

    def _create_document(self, doc: Document):
        """Create a document with optional frontmatter"""
        doc_path = self.vault_path / doc.path
        doc_path.parent.mkdir(parents=True, exist_ok=True)

        content = ""

        # Add frontmatter if metadata provided
        if doc.metadata:
            content += "---\n"
            for key, value in doc.metadata.items():
                if isinstance(value, list):
                    content += f"{key}:\n"
                    for item in value:
                        content += f"  - {item}\n"
                else:
                    content += f"{key}: {value}\n"
            content += "---\n\n"

        content += doc.content

        doc_path.write_text(content)

    def _copy_image(self, img: ImageFile):
        """Copy image file to vault"""
        dest_path = self.vault_path / img.path
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy from test resources
        source_path = Path(__file__).parent / "test_resources" / img.source_path
        shutil.copy(source_path, dest_path)

    def _initialize_vault(self):
        """Initialize vault with zk-chat (creates config, runs initial index)"""
        # This could invoke zk-chat index rebuild
        # or directly create minimal config
        pass
```

#### 4. LLM Validator (`llm_validator.py`)

Implements "LLM as judge" validation:

```python
from pathlib import Path
from typing import List

class LLMValidator:
    """Uses LLM as judge to validate scenario outcomes"""

    def __init__(
        self,
        vault_path: Path,
        gateway: str,
        model: Optional[str] = None
    ):
        self.vault_path = vault_path
        self.gateway = gateway
        self.model = model

    def validate(self, criteria: List[ValidationCriterion]) -> ValidationResult:
        """
        Validate using LLM as judge.

        For each criterion, prompts the agent to check if it's satisfied.
        Parses response to determine pass/fail.
        """
        criteria_results = []

        for criterion in criteria:
            result = self._validate_criterion(criterion)
            criteria_results.append(result)

        # Determine overall pass/fail
        all_passed = all(r["passed"] for r in criteria_results)

        # Generate overall reasoning
        reasoning = self._generate_overall_reasoning(criteria_results)

        return ValidationResult(
            passed=all_passed,
            criteria_results=criteria_results,
            overall_reasoning=reasoning
        )

    def _validate_criterion(self, criterion: ValidationCriterion) -> Dict:
        """Validate a single criterion"""
        # Build validation prompt
        validation_prompt = f"""
You are validating the results of a task. Examine the vault and determine if the following criterion is satisfied:

{criterion.description}

Specific validation instructions:
{criterion.prompt}

Respond with:
- PASS or FAIL
- Your reasoning for the decision

Format your response as:
Result: [PASS/FAIL]
Reasoning: [Your detailed reasoning]
"""

        # Run agent with validation prompt
        runner = AgentRunner(
            vault_path=self.vault_path,
            gateway=self.gateway,
            model=self.model,
            agent_mode="interactive",
            unsafe=False,
            use_git=False
        )

        result = runner.run(validation_prompt, timeout=120)

        # Parse result
        passed = self._parse_validation_response(result.output, criterion)

        return {
            "criterion": criterion.description,
            "passed": passed,
            "reasoning": result.output,
            "raw_output": result.output
        }

    def _parse_validation_response(
        self,
        output: str,
        criterion: ValidationCriterion
    ) -> bool:
        """Parse validation response to determine pass/fail"""
        output_lower = output.lower()

        # Look for explicit PASS/FAIL
        if "result: pass" in output_lower or "result:pass" in output_lower:
            return True
        if "result: fail" in output_lower or "result:fail" in output_lower:
            return False

        # If success keywords provided, check for them
        if criterion.success_keywords:
            keyword_matches = sum(
                1 for keyword in criterion.success_keywords
                if keyword.lower() in output_lower
            )
            # Require majority of keywords present
            return keyword_matches >= len(criterion.success_keywords) / 2

        # Default: look for positive indicators
        positive_indicators = ["success", "correct", "satisfied", "yes", "confirmed"]
        negative_indicators = ["fail", "incorrect", "not satisfied", "no", "missing"]

        positive_count = sum(1 for ind in positive_indicators if ind in output_lower)
        negative_count = sum(1 for ind in negative_indicators if ind in output_lower)

        return positive_count > negative_count

    def _generate_overall_reasoning(self, criteria_results: List[Dict]) -> str:
        """Generate overall reasoning from individual results"""
        passed_count = sum(1 for r in criteria_results if r["passed"])
        total_count = len(criteria_results)

        reasoning = f"Validation Results: {passed_count}/{total_count} criteria passed\n\n"

        for i, result in enumerate(criteria_results, 1):
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            reasoning += f"{i}. {status}: {result['criterion']}\n"

        return reasoning
```

## Test Suites

### 1. Basic Document Operations (basic_operations_integration_spec.py)

**Objective**: Validate reading and writing documents in the Zettelkasten

**Example Scenario Definition** (`scenarios/basic_operations/create_document_scenario.py`):

```python
from zk_chat.integration.scenario_harness import (
    IntegrationScenario, Document, ValidationCriterion
)

def create_document_scenario() -> IntegrationScenario:
    """Scenario: Agent creates a new document about Python programming"""
    return IntegrationScenario(
        name="create_document_with_metadata",
        description="Agent should create a new document with proper metadata",

        initial_documents=[
            Document(
                path="Programming Languages.md",
                content="This vault contains information about programming languages.",
                metadata={"type": "index"}
            )
        ],

        execution_prompt="""
Create a new document called "Python Basics.md" about Python programming.
Include the following content:
- A brief introduction to Python
- Key features (readable syntax, dynamic typing, extensive libraries)
- Common use cases (web development, data science, automation)

Add metadata tags: ["programming", "python", "tutorial"]
""",

        agent_mode="autonomous",
        unsafe=True,
        use_git=True,

        validation_criteria=[
            ValidationCriterion(
                description="Document 'Python Basics.md' exists",
                prompt="""
Check if a document named 'Python Basics.md' exists in the vault.
List all documents to verify.
""",
                success_keywords=["Python Basics.md", "exists", "found"]
            ),
            ValidationCriterion(
                description="Document contains required content sections",
                prompt="""
Read the 'Python Basics.md' document and verify it contains:
1. An introduction to Python
2. Information about key features (syntax, typing, libraries)
3. Common use cases (web, data science, automation)

Does the document cover all these topics adequately?
""",
                success_keywords=["introduction", "features", "use cases", "covers"]
            ),
            ValidationCriterion(
                description="Document has correct metadata tags",
                prompt="""
Read the 'Python Basics.md' document and examine its frontmatter metadata.
Does it include tags for 'programming', 'python', and 'tutorial'?
""",
                success_keywords=["tags", "programming", "python", "tutorial"]
            )
        ]
    )
```

**Test Specification** (`basic_operations_integration.py`):

```python
import pytest
from pathlib import Path
from zk_chat.integration.scenario_harness import ScenarioRunner
from zk_chat.integration.scenarios.basic_operations import (
    create_document_scenario,
    read_document_scenario,
    update_document_scenario,
    rename_document_scenario
)

class DescribeBasicDocumentOperations:
    """Integration tests for basic document read/write operations"""

    @pytest.fixture
    def scenario_runner(self):
        return ScenarioRunner(gateway="ollama")

    def should_create_new_document_with_metadata(self, scenario_runner, tmp_path):
        scenario = create_document_scenario()

        result = scenario_runner.run_scenario(scenario, tmp_path)

        assert result.passed, f"Scenario failed:\n{result.validation_result.overall_reasoning}"
        assert result.execution_result.success, f"Execution failed: {result.execution_result.error}"

    def should_read_existing_document(self, scenario_runner, tmp_path):
        scenario = read_document_scenario()

        result = scenario_runner.run_scenario(scenario, tmp_path)

        assert result.passed, f"Scenario failed:\n{result.validation_result.overall_reasoning}"

    def should_update_existing_document(self, scenario_runner, tmp_path):
        scenario = update_document_scenario()

        result = scenario_runner.run_scenario(scenario, tmp_path)

        assert result.passed, f"Scenario failed:\n{result.validation_result.overall_reasoning}"

    def should_rename_document_and_update_wikilinks(self, scenario_runner, tmp_path):
        scenario = rename_document_scenario()

        result = scenario_runner.run_scenario(scenario, tmp_path)

        assert result.passed, f"Scenario failed:\n{result.validation_result.overall_reasoning}"
```

### 2. RAG Query and Summarization (rag_operations_integration.py)

**Objective**: Validate information retrieval and summarization across documents

**Example Scenario** (`scenarios/rag_operations/summarize_topic_scenario.py`):

```python
def summarize_topic_scenario() -> IntegrationScenario:
    """Scenario: Agent summarizes information about testing across multiple documents"""
    return IntegrationScenario(
        name="summarize_testing_practices",
        description="Agent should gather and summarize information about testing from multiple sources",

        initial_documents=[
            Document(
                path="Unit Testing.md",
                content="""# Unit Testing

Unit testing involves testing individual components in isolation. Benefits include:
- Fast feedback
- Easy debugging
- Regression prevention
- Documentation of behavior

Use mocks to isolate dependencies.""",
                metadata={"tags": ["testing", "unit-tests"]}
            ),
            Document(
                path="Integration Testing.md",
                content="""# Integration Testing

Integration testing validates that components work together correctly. Key aspects:
- Tests real interactions
- Catches integration bugs
- Slower than unit tests
- More realistic scenarios

Use real dependencies when possible.""",
                metadata={"tags": ["testing", "integration-tests"]}
            ),
            Document(
                path="Test-Driven Development.md",
                content="""# Test-Driven Development

TDD is a development approach where tests are written before code:
1. Write a failing test
2. Write minimal code to pass
3. Refactor while keeping tests green

Benefits: Better design, comprehensive coverage, living documentation.""",
                metadata={"tags": ["testing", "tdd", "methodology"]}
            )
        ],

        execution_prompt="""
Please provide a comprehensive summary of testing practices based on the documents in this vault.
Include information about:
- Different types of testing
- Benefits of each approach
- Best practices and methodologies

Create a new document called "Testing Summary.md" with your findings.
""",

        agent_mode="autonomous",
        unsafe=True,
        use_git=True,

        validation_criteria=[
            ValidationCriterion(
                description="Summary document was created",
                prompt="Verify that a document named 'Testing Summary.md' exists in the vault."
            ),
            ValidationCriterion(
                description="Summary covers unit testing",
                prompt="""
Read 'Testing Summary.md' and verify it includes information about unit testing,
such as testing in isolation, using mocks, and fast feedback.
"""
            ),
            ValidationCriterion(
                description="Summary covers integration testing",
                prompt="""
Read 'Testing Summary.md' and verify it includes information about integration testing,
such as testing interactions between components and realistic scenarios.
"""
            ),
            ValidationCriterion(
                description="Summary covers TDD methodology",
                prompt="""
Read 'Testing Summary.md' and verify it mentions Test-Driven Development
and the red-green-refactor cycle.
"""
            ),
            ValidationCriterion(
                description="Summary synthesizes information coherently",
                prompt="""
Read 'Testing Summary.md' and evaluate whether it:
- Coherently integrates information from multiple sources
- Provides a structured overview
- Adds value beyond just concatenating the original documents

Is this a well-structured summary?
"""
            )
        ]
    )
```

### 3. Map of Content Generation (moc_generation_integration.py)

**Objective**: Validate automatic Map of Content (MoC) generation

**Example Scenario** (`scenarios/moc_generation/generate_moc_scenario.py`):

```python
def generate_python_moc_scenario() -> IntegrationScenario:
    """Scenario: Agent generates a Map of Content for Python-related documents"""
    return IntegrationScenario(
        name="generate_python_moc",
        description="Agent should create a structured MoC linking Python-related documents",

        initial_documents=[
            Document(
                path="Python Basics.md",
                content="Introduction to Python syntax, variables, and control flow.",
                metadata={"tags": ["python", "basics"]}
            ),
            Document(
                path="Python Data Structures.md",
                content="Lists, dictionaries, sets, and tuples in Python.",
                metadata={"tags": ["python", "data-structures"]}
            ),
            Document(
                path="Python Functions.md",
                content="Defining functions, parameters, return values, and decorators.",
                metadata={"tags": ["python", "functions"]}
            ),
            Document(
                path="Python Classes.md",
                content="Object-oriented programming in Python with classes and objects.",
                metadata={"tags": ["python", "oop"]}
            ),
            Document(
                path="Python Testing.md",
                content="Using pytest for unit testing Python applications.",
                metadata={"tags": ["python", "testing"]}
            ),
            Document(
                path="JavaScript Basics.md",
                content="Introduction to JavaScript - should not be included in Python MoC.",
                metadata={"tags": ["javascript", "basics"]}
            )
        ],

        execution_prompt="""
Create a Map of Content (MoC) for Python programming.

The MoC should:
- Be named "MOC - Python Programming.md"
- Include an introduction explaining what the MoC covers
- Organize related documents into logical sections (e.g., Fundamentals, Advanced Topics, Tools)
- Use wikilinks [[Document Name]] to link to related documents
- Only include Python-related documents (exclude JavaScript or unrelated topics)
- Include metadata: type: moc, topic: python

Please create this MoC now.
""",

        agent_mode="autonomous",
        unsafe=True,
        use_git=True,

        validation_criteria=[
            ValidationCriterion(
                description="MoC document was created with correct name",
                prompt="""
Check if a document named 'MOC - Python Programming.md' exists in the vault.
List all documents to verify.
"""
            ),
            ValidationCriterion(
                description="MoC includes wikilinks to Python documents",
                prompt="""
Read 'MOC - Python Programming.md' and verify it contains wikilinks to:
- Python Basics
- Python Data Structures
- Python Functions
- Python Classes
- Python Testing

List all wikilinks found in the MoC.
"""
            ),
            ValidationCriterion(
                description="MoC excludes unrelated documents",
                prompt="""
Read 'MOC - Python Programming.md' and verify it does NOT contain links
to JavaScript or other non-Python topics.

Does it correctly exclude 'JavaScript Basics.md'?
"""
            ),
            ValidationCriterion(
                description="MoC has logical structure and sections",
                prompt="""
Read 'MOC - Python Programming.md' and evaluate its structure.
Does it:
- Have a clear introduction?
- Organize content into logical sections/categories?
- Use proper Markdown heading hierarchy?

Is the structure logical and helpful?
"""
            ),
            ValidationCriterion(
                description="MoC has correct metadata",
                prompt="""
Read 'MOC - Python Programming.md' and check its frontmatter metadata.
Does it include:
- type: moc (or similar indicator it's a Map of Content)
- topic: python (or similar topic identifier)
"""
            )
        ]
    )
```

### 4. Image Caption Generation (image_operations_integration.py)

**Objective**: Validate image analysis and caption generation

**Example Scenario** (`scenarios/image_operations/generate_caption_scenario.py`):

```python
def generate_caption_scenario() -> IntegrationScenario:
    """Scenario: Agent generates captions for images referenced in documents"""
    return IntegrationScenario(
        name="generate_image_captions",
        description="Agent should analyze images and add descriptive captions to documents",

        initial_documents=[
            Document(
                path="Architecture Design.md",
                content="""# Architecture Design

Here is our system architecture diagram:

![Architecture Diagram](images/architecture.png)

The diagram shows the main components of our system.
""",
                metadata={"tags": ["architecture", "design"]}
            )
        ],

        initial_images=[
            ImageFile(
                path="images/architecture.png",
                source_path="test_architecture_diagram.png"
            )
        ],

        execution_prompt="""
Please analyze the image referenced in 'Architecture Design.md' and add a detailed caption
below the image describing what it shows. The caption should:
- Identify the main components
- Describe the relationships between components
- Mention any notable patterns or structures

Update the document with the caption.
""",

        agent_mode="autonomous",
        unsafe=True,
        use_git=True,

        validation_criteria=[
            ValidationCriterion(
                description="Document was updated",
                prompt="""
Read 'Architecture Design.md' and check if it has been modified to include
a caption or description below the image reference.
"""
            ),
            ValidationCriterion(
                description="Caption describes image content",
                prompt="""
Read 'Architecture Design.md' and examine the caption that was added.
Does the caption provide meaningful information about what the diagram shows?
Does it mention components, relationships, or architectural patterns?
"""
            ),
            ValidationCriterion(
                description="Caption is appropriately positioned",
                prompt="""
Read 'Architecture Design.md' and verify the caption is positioned
appropriately (typically immediately after the image reference).
Is the formatting clean and readable?
"""
            )
        ]
    )
```

### 5. Screenshot/Whiteboard Analysis (image_operations_integration.py)

**Objective**: Validate complex image analysis workflows

**Example Scenario** (`scenarios/image_operations/analyze_whiteboard_scenario.py`):

```python
def analyze_whiteboard_scenario() -> IntegrationScenario:
    """Scenario: Agent analyzes whiteboard photos from a brainstorming session"""
    return IntegrationScenario(
        name="analyze_whiteboard_brainstorm",
        description="Agent should extract and organize information from whiteboard photos",

        initial_documents=[
            Document(
                path="Brainstorming Session.md",
                content="""# Brainstorming Session - Product Features

Date: 2025-10-01

We held a brainstorming session to discuss new product features.
Whiteboard photos are stored in the images folder.

## Photos

![Whiteboard 1](images/whiteboard_1.jpg)
![Whiteboard 2](images/whiteboard_2.jpg)

## Analysis

TBD
""",
                metadata={"tags": ["meeting", "brainstorming"]}
            )
        ],

        initial_images=[
            ImageFile(
                path="images/whiteboard_1.jpg",
                source_path="test_whiteboard_features.jpg"
            ),
            ImageFile(
                path="images/whiteboard_2.jpg",
                source_path="test_whiteboard_priorities.jpg"
            )
        ],

        execution_prompt="""
Please analyze the whiteboard photos in 'Brainstorming Session.md' and extract
all the information you can see. Then:

1. Create a structured summary of the brainstorming session
2. Extract any lists, diagrams, or key points visible on the whiteboards
3. Organize the information into logical sections
4. Replace the "TBD" section in the document with your analysis

The analysis should be comprehensive and capture all visible information.
""",

        agent_mode="autonomous",
        unsafe=True,
        use_git=True,

        validation_criteria=[
            ValidationCriterion(
                description="Document was updated with analysis",
                prompt="""
Read 'Brainstorming Session.md' and verify that the 'Analysis' section
has been replaced with actual content (not just 'TBD').
"""
            ),
            ValidationCriterion(
                description="Analysis extracts text and ideas from images",
                prompt="""
Read the analysis in 'Brainstorming Session.md'.
Does it contain specific information that would have been extracted from
the whiteboard photos? Look for:
- Feature ideas or product suggestions
- Lists or bullet points
- Priorities or categories
- Any structured information

Does the analysis show evidence of actually examining the images?
"""
            ),
            ValidationCriterion(
                description="Analysis is well-structured",
                prompt="""
Read the analysis in 'Brainstorming Session.md'.
Is the information organized in a logical, readable way?
Does it use appropriate Markdown formatting (headings, lists, etc.)?
"""
            ),
            ValidationCriterion(
                description="Analysis synthesizes information from multiple images",
                prompt="""
Read the analysis in 'Brainstorming Session.md'.
Does it show evidence of analyzing BOTH whiteboard images?
Does it integrate or relate information from the different photos?
"""
            )
        ]
    )
```

## Test Runner Script

Create a dedicated script for running integration tests:

```bash
#!/bin/bash
# scripts/run_integration_tests.sh

# Integration Test Runner for zk-chat
#
# Usage:
#   ./scripts/run_integration_tests.sh [ollama|openai|auto]
#
# Examples:
#   ./scripts/run_integration_tests.sh         # Auto-detect (checks for OPENAI_API_KEY)
#   ./scripts/run_integration_tests.sh auto    # Explicit auto-detect
#   ./scripts/run_integration_tests.sh ollama  # Force Ollama
#   ./scripts/run_integration_tests.sh openai  # Force OpenAI
#
# Environment variables:
#   ZK_TEST_GATEWAY      - Override gateway selection (ollama, openai, or auto)
#   ZK_TEST_MODEL        - Specify text model to use
#   ZK_TEST_VISUAL_MODEL - Specify visual model to use
#   OPENAI_API_KEY       - OpenAI API key (auto-detects OpenAI if present)

set -e  # Exit on error

echo "======================================"
echo "zk-chat Integration Test Suite"
echo "======================================"
echo ""

# Ensure we're in the project root
cd "$(dirname "$0")/.."

# Determine gateway
GATEWAY="${1:-${ZK_TEST_GATEWAY:-auto}}"

# Auto-detect gateway if set to 'auto'
if [ "$GATEWAY" = "auto" ]; then
    if [ -n "${OPENAI_API_KEY}" ]; then
        GATEWAY="openai"
        echo "Auto-detected: OpenAI (OPENAI_API_KEY is set)"
    else
        GATEWAY="ollama"
        echo "Auto-detected: Ollama (no OPENAI_API_KEY found)"
    fi
    echo ""
fi

# Validate gateway
if [ "$GATEWAY" != "ollama" ] && [ "$GATEWAY" != "openai" ]; then
    echo "Error: Gateway must be 'ollama' or 'openai'"
    echo "Usage: $0 [ollama|openai]"
    exit 1
fi

echo "Selected gateway: $GATEWAY"
echo ""

# Gateway-specific setup and validation
if [ "$GATEWAY" = "ollama" ]; then
    echo "Checking Ollama availability..."
    if ! command -v ollama &> /dev/null; then
        echo "Error: Ollama command not found. Please install Ollama."
        echo "Visit: https://ollama.com/"
        exit 1
    fi

    # Check if Ollama is running
    if ! curl -s http://localhost:11434/api/tags &> /dev/null; then
        echo "Error: Ollama is not running. Please start Ollama."
        echo "Run: ollama serve"
        exit 1
    fi

    echo "✓ Ollama is running"

    # Set default models if not already set
    if [ -z "${ZK_TEST_MODEL}" ]; then
        export ZK_TEST_MODEL="qwen2.5:32b"
        echo "Using default text model: $ZK_TEST_MODEL"
    else
        echo "Using custom text model: $ZK_TEST_MODEL"
    fi

    if [ -z "${ZK_TEST_VISUAL_MODEL}" ]; then
        export ZK_TEST_VISUAL_MODEL="llama3.2-vision:11b"
        echo "Using default visual model: $ZK_TEST_VISUAL_MODEL"
    else
        echo "Using custom visual model: $ZK_TEST_VISUAL_MODEL"
    fi

    echo ""
    echo "Testing with local Ollama models:"
    echo "  - No API costs"
    echo "  - May be slower depending on hardware"
    echo ""

elif [ "$GATEWAY" = "openai" ]; then
    echo "Checking OpenAI configuration..."

    if [ -z "${OPENAI_API_KEY}" ]; then
        echo "Error: OPENAI_API_KEY environment variable is not set."
        echo "Please set your OpenAI API key:"
        echo "  export OPENAI_API_KEY=your_key_here"
        exit 1
    fi

    echo "✓ OpenAI API key is configured"

    # Set default models if not already set
    if [ -z "${ZK_TEST_MODEL}" ]; then
        export ZK_TEST_MODEL="gpt-4o"
        echo "Using default text model: $ZK_TEST_MODEL"
    else
        echo "Using custom text model: $ZK_TEST_MODEL"
    fi

    if [ -z "${ZK_TEST_VISUAL_MODEL}" ]; then
        export ZK_TEST_VISUAL_MODEL="gpt-4o"
        echo "Using default visual model: $ZK_TEST_VISUAL_MODEL"
    else
        echo "Using custom visual model: $ZK_TEST_VISUAL_MODEL"
    fi

    echo ""
    echo "⚠️  WARNING: Testing with OpenAI API"
    echo "  - This will incur API costs"
    echo "  - Estimated cost: \$0.50-\$2.00 per full test run"
    echo "  - Cost varies by model and test coverage"
    echo ""
    read -p "Continue with OpenAI? [y/N]: " confirm

    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Cancelled."
        exit 0
    fi
    echo ""
fi

export ZK_TEST_GATEWAY="$GATEWAY"

# Activate virtual environment if needed
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

echo "Starting integration tests..."
echo "======================================"
echo ""

# Run integration tests with detailed output
pytest integration_tests/ \
    --spec \
    --tb=short \
    --showlocals \
    --color=yes \
    -v \
    --capture=no

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✓ All integration tests passed!"
    echo "======================================"
    exit 0
else
    echo ""
    echo "======================================"
    echo "✗ Integration tests failed!"
    echo "======================================"
    exit 1
fi
```

## Test Data Requirements

### Test Resource Images

Create a library of test images in `zk_chat/integration/test_resources/`:

1. **test_architecture_diagram.png** - Simple architecture diagram (boxes and arrows)
2. **test_whiteboard_features.jpg** - Whiteboard with feature list
3. **test_whiteboard_priorities.jpg** - Whiteboard with priorities/rankings
4. **test_code_screenshot.png** - Screenshot of code
5. **test_presentation_slide.png** - Presentation slide with text

These images will be copied into test vaults as needed by scenario definitions.

### Pytest Configuration (`conftest.py`)

```python
import pytest
from pathlib import Path
from zk_chat.integration.scenario_harness import ScenarioRunner

@pytest.fixture(scope="session")
def test_resources_dir():
    """Path to test resource files"""
    return Path(__file__).parent / "test_resources"

```python
@pytest.fixture
def scenario_runner():
    """Create a scenario runner for tests"""
    # Gateway must be explicitly set via environment variable
    gateway = os.environ.get("ZK_TEST_GATEWAY")

    if not gateway:
        pytest.skip(
            "ZK_TEST_GATEWAY environment variable not set. "
            "Set to 'ollama' or 'openai' before running integration tests."
        )

    if gateway not in ["ollama", "openai"]:
        pytest.fail(f"Invalid ZK_TEST_GATEWAY: {gateway}. Must be 'ollama' or 'openai'.")

    # For OpenAI, verify API key is set
    if gateway == "openai" and not os.environ.get("OPENAI_API_KEY"):
        pytest.skip(
            "OPENAI_API_KEY environment variable not set. "
            "Required when using openai gateway."
        )

    model = os.environ.get("ZK_TEST_MODEL", None)

    return ScenarioRunner(gateway=gateway, model=model)# Pytest configuration for better output
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
        # Mark all integration tests as slow
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.slow)

        # Mark tests requiring visual models
        if "image" in item.name.lower() or "visual" in item.name.lower():
            item.add_marker(pytest.mark.requires_visual)
```

## Running Integration Tests

### Gateway Configuration

Integration tests support **smart defaults** for gateway selection:

1. **Explicit**: Set `ZK_TEST_GATEWAY` environment variable
2. **OpenAI auto-detect**: Uses OpenAI if `OPENAI_API_KEY` is set
3. **Ollama fallback**: Uses Ollama if no API key present

### Default Models

When models are not explicitly specified, these defaults are used:

| Gateway | Text Model | Visual Model |
|---------|------------|--------------|
| **OpenAI** | `gpt-4o` | `gpt-4o` |
| **Ollama** | `qwen2.5:32b` | `llama3.2-vision:11b` |

### Quick Start Examples

#### Default Behavior (Auto-detect Gateway)

```bash
# If OPENAI_API_KEY is set, uses OpenAI with gpt-4o
# Otherwise uses Ollama with qwen2.5:32b
pytest integration_tests/ --spec -v
```

#### Explicit Ollama

```bash
# Force Ollama usage
export ZK_TEST_GATEWAY=ollama

# Run tests (uses qwen2.5:32b and llama3.2-vision:11b by default)
pytest integration_tests/ --spec -v

# Override default models
export ZK_TEST_MODEL=qwen2.5:14b
export ZK_TEST_VISUAL_MODEL=llama3.2-vision:11b
pytest integration_tests/ --spec -v
```

#### Explicit OpenAI

```bash
# Force OpenAI usage
export ZK_TEST_GATEWAY=openai
export OPENAI_API_KEY=your_api_key_here

# Run tests (uses gpt-4o by default)
pytest integration_tests/ --spec -v

# Override default models
export ZK_TEST_MODEL=gpt-4o-mini
pytest integration_tests/ --spec -v
```

### Gateway Characteristics

| Aspect | Ollama | OpenAI |
|--------|---------|---------|
| **Cost** | Free | ~$0.50-$2.00 per run |
| **Speed** | Slower (hardware dependent) | Faster |
| **Privacy** | Completely local | Data sent to OpenAI |
| **Reliability** | Depends on model/hardware | More consistent |
| **Setup** | Requires Ollama + models | Requires API key |
| **Default Models** | qwen2.5:32b, llama3.2-vision:11b | gpt-4o |

### Pre-Release Validation

Before each release, run:

```bash
# Option 1: Use dedicated script (handles gateway selection)
./scripts/run_integration_tests.sh

# Option 2: Direct pytest (auto-detects gateway)
pytest integration_tests/ --spec -v

# Option 3: Run specific test suite
pytest integration_tests/moc_generation_integration.py --spec -v

# Option 4: Explicit OpenAI for consistency
export ZK_TEST_GATEWAY=openai
pytest integration_tests/ --spec -v
```

### CI/CD Integration

Add to GitHub Actions workflow (using OpenAI for consistent, reliable results):

```yaml
# .github/workflows/integration-tests.yml
name: Integration Tests

on:
  # Only run on schedule or manual trigger to control costs
  schedule:
    - cron: '0 2 * * 0'  # Weekly on Sunday at 2 AM UTC
  workflow_dispatch:  # Allow manual triggering
    inputs:
      gateway:
        description: 'Gateway to use (ollama or openai)'
        required: true
        default: 'openai'
        type: choice
        options:
          - openai
          - ollama

jobs:
  integration-test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -e ".[dev]"

    # For Ollama gateway (if selected)
    - name: Install Ollama
      if: ${{ github.event.inputs.gateway == 'ollama' || github.event_name == 'schedule' }}
      run: |
        curl -fsSL https://ollama.com/install.sh | sh
        ollama serve &
        sleep 5
        ollama pull qwen2.5:14b

    - name: Run integration tests with Ollama
      if: ${{ github.event.inputs.gateway == 'ollama' }}
      env:
        ZK_TEST_GATEWAY: ollama
        ZK_TEST_MODEL: qwen2.5:32b
        ZK_TEST_VISUAL_MODEL: llama3.2-vision:11b
      run: |
        pytest integration_tests/ --spec -v --tb=short

    # For OpenAI gateway (if selected or default)
    - name: Run integration tests with OpenAI
      if: ${{ github.event.inputs.gateway == 'openai' || github.event_name == 'schedule' }}
      env:
        ZK_TEST_GATEWAY: openai
        OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
        ZK_TEST_MODEL: gpt-4o
        ZK_TEST_VISUAL_MODEL: gpt-4o
      run: |
        pytest integration_tests/ --spec -v --tb=short
```

**Note on CI/CD Strategy:**

- **Scheduled runs**: Use weekly schedule to control costs
- **Manual trigger**: Allow on-demand runs with gateway selection
- **Not on every commit**: Too expensive and slow for continuous testing
- **OpenAI for reliability**: Use OpenAI in CI for more consistent results
- **Secrets management**: Store `OPENAI_API_KEY` in GitHub repository secrets

## Release Process Updates

Update `.github/copilot-instructions.md` release section:

```markdown
### Pre-Release Integration Testing

Before preparing any release:

1. **Set up Testing Gateway** (optional - auto-detects):
   ```bash
   # Auto-detect (recommended): Uses OpenAI if OPENAI_API_KEY set, else Ollama
   # No explicit configuration needed

   # OR explicitly choose:
   export ZK_TEST_GATEWAY=openai  # Recommended for pre-release
   export OPENAI_API_KEY=your_key_here

   # OR force Ollama:
   export ZK_TEST_GATEWAY=ollama
   ```

2. **Run Integration Test Suite**:
   ```bash
   ./scripts/run_integration_tests.sh
   # Or directly:
   pytest integration_tests/ --spec -v
   ```

3. **Verify All Tests Pass**:
   - All integration tests must pass
   - Review any warnings or deprecations
   - Address any test failures before proceeding
   - If using Ollama and tests fail, consider re-running with OpenAI for validation

4. **Document Test Results**:
   - Note which gateway was used (ollama or openai)
   - Note any new integration tests added
   - Document any test failures and resolutions
   - Include test coverage metrics if available

5. **Proceed with Release Preparation**:
   - Only proceed to release preparation after all tests pass
   - Include integration test results in release notes if relevant
   - Note: If only tested with Ollama, consider mentioning this in release notes
```

## Implementation Timeline

### Phase 1: Core Infrastructure (2-3 days)
- Implement `scenario_harness.py` with core data structures
- Implement `agent_runner.py` for programmatic agent invocation
- Implement `vault_builder.py` for test vault creation
- Implement `llm_validator.py` for LLM-as-judge validation
- Set up pytest configuration and test resources directory

### Phase 2: First Scenario & Validation (2-3 days)
- Create test resource images
- Implement first complete scenario (e.g., create document)
- Implement first test spec using the scenario
- Validate end-to-end flow works correctly
- Refine infrastructure based on learnings

### Phase 3: Basic Operations Scenarios (2-3 days)
- Implement remaining document operation scenarios
- Add read, update, rename scenarios
- Test and validate each scenario
- Refine validation criteria based on actual LLM responses

### Phase 4: Advanced Scenarios (3-4 days)
- Implement RAG/summarization scenarios
- Implement MoC generation scenarios
- Implement image operation scenarios (caption generation, whiteboard analysis)
- Test and validate advanced workflows

### Phase 5: Polish and Documentation (1-2 days)
- Create test runner script
- Update documentation (README, release process)
- Add CI/CD integration
- Create troubleshooting guide

**Total Estimated Time: 10-15 days**

### Implementation Priority Order

1. **Critical Path**: scenario_harness.py → agent_runner.py → vault_builder.py → llm_validator.py
2. **First Validation**: One complete scenario end-to-end
3. **Expand Coverage**: Additional scenarios in order of complexity
4. **Polish**: Documentation and automation

## Benefits

1. **Confidence**: Know that real workflows work before releasing (using actual LLM calls)
2. **Regression Prevention**: Catch breaking changes in complex end-to-end interactions
3. **Documentation**: Scenarios serve as executable documentation of intended behavior
4. **Quality Assurance**: Systematic validation using subjective "LLM as judge" criteria
5. **Faster Debugging**: When tests fail, validation reasoning explains exactly what's wrong
6. **Realistic Testing**: Tests exercise the full system including actual agent reasoning
7. **Maintainable**: Declarative scenario definitions are easier to update than imperative test code

## Future Enhancements

1. **Performance Testing**: Add timing assertions to catch performance regressions
2. **Load Testing**: Test with larger vaults (1000+ documents)
3. **Concurrent Operations**: Test handling of multiple simultaneous operations
4. **Plugin Integration**: Test plugin installation and usage
5. **UI Testing**: Add integration tests for the GUI component
6. **Real LLM Tests**: Optional tests using actual LLM calls (marked as slow)

## Important Notes

### Test Characteristics

- **Slow**: Integration tests make real LLM calls and are inherently slow
  - Ollama: 45-180 seconds per scenario (depends on hardware and model)
  - OpenAI: 30-90 seconds per scenario (generally faster)
- **Non-Deterministic**: LLM responses vary, so tests validate behavior subjectively using "LLM as judge"
- **Isolated**: Each test creates its own vault in tmp_path, ensuring no shared state
- **End-to-End**: Tests exercise the complete system including agent reasoning and tool execution
- **Realistic**: Test data should be realistic but minimal to keep execution time reasonable

### Test Execution Considerations

1. **Gateway Selection**:
   - **Must** be explicitly chosen via `ZK_TEST_GATEWAY` environment variable
   - Tests will be skipped if gateway not configured
   - Different gateways have different characteristics (see table above)

2. **Cost** (OpenAI only):
   - Full test suite: ~$0.50-$2.00 per run (varies by model)
   - Single test: ~$0.05-$0.20
   - Validation queries also incur costs

3. **Time**:
   - Ollama full suite: 15-40 minutes (depends on hardware)
   - OpenAI full suite: 10-25 minutes
   - Single scenario: 1-3 minutes

4. **Reliability**:
   - Network issues can cause failures (both gateways)
   - Ollama: Model performance varies by hardware
   - OpenAI: Generally more consistent results
   - LLM reasoning variations may cause occasional false negatives

5. **Environment Requirements**:
   - Ollama: Must be running locally (`ollama serve`)
   - OpenAI: Must have valid API key with available credits
   - Both: Adequate model available (installed for Ollama, authorized for OpenAI)

### When to Run

- **Required**: Before every release
- **Recommended**: After major changes to agent, tools, or core components
- **Optional**: During development (run specific scenarios instead of full suite)
- **CI/CD**: Consider running on schedule (nightly) rather than every commit

### Debugging Failed Tests

When a test fails:

1. Check execution_result.error for agent execution errors
2. Read validation_result.overall_reasoning for detailed validation explanation
3. Examine the test vault in tmp_path (use --keep-tmp-path pytest option)
4. Check individual criteria_results for specific validation failures
5. Re-run the specific scenario with verbose logging enabled

### Configuration

Set environment variables to control test behavior:

```bash
# === REQUIRED: Choose gateway ===
export ZK_TEST_GATEWAY=ollama  # or openai

# === For Ollama ===
export ZK_TEST_MODEL=qwen2.5:14b  # Optional: defaults to model in config
# Ensure Ollama is running: ollama serve

# === For OpenAI ===
export OPENAI_API_KEY=your_key_here  # Required for OpenAI
export ZK_TEST_MODEL=gpt-4  # Optional: specify model

# === Additional Options ===

# Keep temp directories for debugging
pytest --keep-tmp-path

# Run only fast tests (skip slow integration tests)
pytest -m "not slow"

# Run specific scenario
pytest zk_chat/integration/basic_operations_integration_spec.py::DescribeBasicDocumentOperations::should_create_new_document_with_metadata -v

# Increase timeout for slow models
export ZK_TEST_TIMEOUT=600  # seconds, default is 300
```

### Choosing Between Gateways

| Consideration | Ollama | OpenAI |
|--------------|---------|---------|
| **Cost** | Free | ~$0.50-$2.00 per test run |
| **Speed** | Slower (varies by hardware) | Faster |
| **Privacy** | Completely local | Data sent to OpenAI |
| **Reliability** | Depends on model/hardware | Generally more consistent |
| **Setup** | Requires Ollama installed | Requires API key |
| **Internet** | Not required | Required |
| **Best For** | Development, local testing | Pre-release validation, CI/CD |

**Recommendation**:
- Use **Ollama** during development and frequent testing
- Use **OpenAI** for final pre-release validation and CI/CD
