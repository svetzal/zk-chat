"""
Scenario: Image analysis and description.

Tests the agent's ability to analyze an image and provide a description.
"""
from integration_tests.scenario_harness import (
    IntegrationScenario,
    Document,
    ImageFile,
    ValidationCriterion
)


def analyze_architecture_diagram_scenario() -> IntegrationScenario:
    """
    Scenario: Agent analyzes an architecture diagram image and describes it.

    Image: zk-chat-architecture.png
    Expected: A diagram showing system components and their relationships

    You should place an architecture diagram image in:
    integration_tests/test_resources/zk-chat-architecture.png

    The image should show:
    - Multiple components/boxes
    - Connections/arrows between components
    - Labels or text describing components
    - A clear architectural pattern or structure
    """
    return IntegrationScenario(
        name="analyze_architecture_diagram",
        description="Agent should analyze an architecture diagram and provide a detailed description",

        initial_documents=[
            Document(
                path="Architecture Notes.md",
                content="""# System Architecture Notes

We have created an architecture diagram showing our system design.

![Architecture Diagram](images/architecture_diagram.png)

## Description

TBD - Please analyze the diagram above and provide a detailed description of what it shows.
""",
                metadata={"tags": ["architecture", "documentation"]}
            )
        ],

        initial_images=[
            ImageFile(
                path="images/architecture_diagram.png",
                source_path="zk-chat-architecture.png"
            )
        ],

        execution_prompt="""
Please analyze the architecture diagram referenced in 'Architecture Notes.md'.

Look at the image carefully and provide a detailed description that includes:
1. What components or systems are shown
2. How they are connected or related
3. Any patterns or architectural style visible
4. Key characteristics or notable features

Replace the "TBD" section in the document with your analysis.
Use the --unsafe flag to modify the document.
""",

        agent_mode="autonomous",
        unsafe=True,
        use_git=True,

        validation_criteria=[
            ValidationCriterion(
                description="Document was updated with analysis",
                prompt="""
Read 'Architecture Notes.md' and verify that the 'Description' section
has been updated with actual content (not just 'TBD').

Does the document contain an analysis of the diagram?
""",
                success_keywords=["analysis", "updated", "description"]
            ),
            ValidationCriterion(
                description="Analysis describes components",
                prompt="""
Read the analysis in 'Architecture Notes.md'.

Does the description mention specific components, systems, or parts
visible in the diagram? Look for references to boxes, modules,
services, or other structural elements.

""",
                success_keywords=["components", "systems", "elements"]
            ),
            ValidationCriterion(
                description="Analysis describes relationships",
                prompt="""
Read the analysis in 'Architecture Notes.md'.

Does the description explain how components are connected or how they
interact? Look for mentions of connections, arrows, data flow,
or relationships between parts.
""",
                success_keywords=["connections", "relationships", "interact", "flow"]
            ),
            ValidationCriterion(
                description="Analysis is substantive",
                prompt="""
Read the analysis in 'Architecture Notes.md'.

Is the analysis substantive and detailed (at least 2-3 sentences)?
Does it provide meaningful information about the diagram rather than
just generic statements?

Does it show evidence of actually examining the image?
""",
                success_keywords=["detailed", "specific", "shows"]
            )
        ]
    )
