"""
LLM validator for "LLM as judge" validation.

Uses the agent to validate that scenario outcomes meet criteria.
"""
from pathlib import Path
from typing import Any

from pydantic import BaseModel

from integration_tests.agent_runner import AgentRunner


class ValidationResult(BaseModel):
    """Result of validation"""
    passed: bool
    criteria_results: list[dict[str, Any]]
    overall_reasoning: str

    def merge(self, other: 'ValidationResult') -> 'ValidationResult':
        """Merge with another validation result"""
        return ValidationResult(
            passed=self.passed and other.passed,
            criteria_results=self.criteria_results + other.criteria_results,
            overall_reasoning=f"{self.overall_reasoning}\n\n{other.overall_reasoning}"
        )


class LLMValidator:
    """Uses LLM as judge to validate scenario outcomes"""

    def __init__(
        self,
        vault_path: Path,
        gateway: str,
        model: str | None = None
    ):
        self.vault_path = vault_path
        self.gateway = gateway
        self.model = model

    def validate(self, criteria: list) -> ValidationResult:
        """
        Validate using LLM as judge.

        For each criterion, prompts the agent to check if it's satisfied.
        Parses response to determine pass/fail.
        """
        criteria_results = []

        for criterion in criteria:
            result = self._validate_criterion(criterion)
            criteria_results.append(result)

        all_passed = all(r["passed"] for r in criteria_results)

        reasoning = self._generate_overall_reasoning(criteria_results)

        return ValidationResult(
            passed=all_passed,
            criteria_results=criteria_results,
            overall_reasoning=reasoning
        )

    def _validate_criterion(self, criterion) -> dict:
        """Validate a single criterion"""
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

        runner = AgentRunner(
            vault_path=self.vault_path,
            gateway=self.gateway,
            model=self.model,
            agent_mode="interactive"
        )

        result = runner.run(validation_prompt, timeout=120)

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
        criterion
    ) -> bool:
        """Parse validation response to determine pass/fail"""
        output_lower = output.lower()

        if "result: pass" in output_lower or "result:pass" in output_lower:
            return True
        if "result: fail" in output_lower or "result:fail" in output_lower:
            return False

        if criterion.success_keywords:
            keyword_matches = sum(
                1 for keyword in criterion.success_keywords
                if keyword.lower() in output_lower
            )
            return keyword_matches >= len(criterion.success_keywords) / 2

        positive_indicators = ["success", "correct", "satisfied", "yes", "confirmed"]
        negative_indicators = ["fail", "incorrect", "not satisfied", "no", "missing"]

        positive_count = sum(1 for ind in positive_indicators if ind in output_lower)
        negative_count = sum(1 for ind in negative_indicators if ind in output_lower)

        return positive_count > negative_count

    def _generate_overall_reasoning(self, criteria_results: list[dict]) -> str:
        """Generate overall reasoning from individual results"""
        passed_count = sum(1 for r in criteria_results if r["passed"])
        total_count = len(criteria_results)

        reasoning = f"Validation Results: {passed_count}/{total_count} criteria passed\n\n"

        for i, result in enumerate(criteria_results, 1):
            status = "✓ PASS" if result["passed"] else "✗ FAIL"
            reasoning += f"{i}. {status}: {result['criterion']}\n"

        return reasoning
