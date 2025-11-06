"""
Scenario harness for integration tests.

Provides declarative way to define and execute integration test scenarios.
"""
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from integration_tests.agent_runner import AgentRunner, ExecutionResult
from integration_tests.llm_validator import LLMValidator, ValidationResult
from integration_tests.vault_builder import VaultBuilder


class Document(BaseModel):
    """Represents a document to be created in test vault"""
    path: str
    content: str
    metadata: dict[str, Any] | None = None


class ImageFile(BaseModel):
    """Represents an image file to be placed in test vault"""
    path: str
    source_path: str


class ValidationCriterion(BaseModel):
    """A single validation criterion"""
    description: str
    prompt: str
    success_keywords: list[str] | None = None


class IntegrationScenario(BaseModel):
    """Complete specification of an integration test scenario"""
    name: str
    description: str
    initial_documents: list[Document]
    execution_prompt: str
    initial_images: list[ImageFile] | None = None
    agent_mode: str = "interactive"  # Note: For documentation only; execution always uses agent mode
    validation_criteria: list[ValidationCriterion] | None = None
    custom_validation: Callable | None = Field(default=None, exclude=True)


class ScenarioResult(BaseModel):
    """Complete result of scenario execution and validation"""
    scenario_name: str
    execution_result: ExecutionResult
    validation_result: ValidationResult

    @property
    def passed(self) -> bool:
        return self.execution_result.success and self.validation_result.passed


class ScenarioRunner:
    """Executes integration scenarios"""

    def __init__(self, gateway: str, model: str, visual_model: str | None = None):
        self.gateway = gateway
        self.model = model
        self.visual_model = visual_model

    def run_scenario(self, scenario: IntegrationScenario, tmp_path: Path) -> ScenarioResult:
        """
        Execute a complete integration scenario.

        Returns ScenarioResult with pass/fail and details.
        """
        vault_path = self._build_vault(scenario, tmp_path)

        execution_result = self._execute_agent(scenario, vault_path)

        validation_result = self._validate_scenario(scenario, vault_path, execution_result)

        if scenario.custom_validation:
            custom_result = scenario.custom_validation(vault_path, execution_result)
            validation_result = validation_result.merge(custom_result)

        return ScenarioResult(
            scenario_name=scenario.name,
            execution_result=execution_result,
            validation_result=validation_result
        )

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
            visual_model=self.visual_model,
            agent_mode=scenario.agent_mode
        )
        return runner.run(scenario.execution_prompt)

    def _validate_scenario(
        self,
        scenario: IntegrationScenario,
        vault_path: Path,
        execution_result: ExecutionResult
    ) -> ValidationResult:
        """Validate scenario using LLM as judge"""
        if not scenario.validation_criteria:
            return ValidationResult(
                passed=True,
                criteria_results=[],
                overall_reasoning="No validation criteria specified - execution success is sufficient"
            )

        validator = LLMValidator(
            vault_path=vault_path,
            gateway=self.gateway,
            model=self.model
        )
        return validator.validate(scenario.validation_criteria)
