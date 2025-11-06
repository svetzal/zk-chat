"""
Integration tests for image operations.

Tests the agent's ability to analyze and describe images.
"""

from integration_tests.scenarios.image_operations.analyze_image_scenario import analyze_architecture_diagram_scenario


class DescribeImageAnalysis:
    """Integration tests for image analysis capabilities"""

    def should_analyze_architecture_diagram(self, scenario_runner, tmp_path):
        """
        Test that the agent can analyze an architecture diagram image.

        This test:
        1. Creates a vault with a document referencing an image
        2. Asks the agent to analyze the image and update the document
        3. Validates that the analysis was completed and is substantive
        """
        scenario = analyze_architecture_diagram_scenario()

        result = scenario_runner.run_scenario(scenario, tmp_path)

        assert result.execution_result.success, \
            f"Execution failed: {result.execution_result.error}"

        assert result.passed, \
            f"Scenario validation failed:\n{result.validation_result.overall_reasoning}"
