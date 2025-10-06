# Integration Test Resources

This directory contains test images and other resources used by integration tests.

## Required Test Images

### Architecture Diagram (`test_architecture_diagram.png`)

**Purpose**: Tests the agent's ability to analyze architecture diagrams.

**Required characteristics:**
- Shows a system architecture or component diagram
- Contains multiple components/boxes/modules
- Has connections/arrows showing relationships
- Includes labels or text describing components
- Demonstrates a clear architectural pattern

**Suggested content:**
- Microservices architecture diagram
- Client-server architecture
- Layered architecture (UI, Business Logic, Data)
- Component diagram with databases, services, APIs
- Any technical diagram showing system structure

**Used by:**
- `integration_tests/scenarios/image_operations/analyze_image_scenario.py`
- Test: `should_analyze_architecture_diagram`

**What the test validates:**
- Agent can see and describe components
- Agent can identify relationships/connections
- Agent provides substantive analysis (not just generic description)
- Agent successfully updates document with findings

## Adding Your Own Test Image

1. **Prepare the image:**
   - PNG, JPG, or common image format
   - Reasonable size (under 5MB recommended)
   - Clear and readable

2. **Place in this directory:**
   ```
   integration_tests/test_resources/test_architecture_diagram.png
   ```

3. **Run the test:**
   ```bash
   # With auto-detected gateway
   pytest integration_tests/image_operations_integration.py -v
   
   # With explicit gateway
   export ZK_TEST_GATEWAY=ollama
   pytest integration_tests/image_operations_integration.py -v
   ```

## Example: Creating a Simple Test Diagram

If you don't have an architecture diagram handy, you can:

1. **Draw one** using any tool (draw.io, Excalidraw, Lucidchart, etc.)
2. **Screenshot an existing diagram** from documentation or tutorials
3. **Use a simple sketch** - even hand-drawn and photographed works

**Minimum elements:**
- 3-5 labeled boxes (e.g., "Frontend", "API", "Database")
- Arrows showing connections
- Some indication of data flow or relationships

The test is designed to be flexible - it validates that the agent provides meaningful analysis, not that it matches a specific template.

## Future Test Images

As more scenarios are added, additional images may be required:

- `test_whiteboard_features.jpg` - Whiteboard photo with brainstorming notes
- `test_whiteboard_priorities.jpg` - Whiteboard with prioritized list
- `test_code_screenshot.png` - Screenshot of code
- `test_presentation_slide.png` - Presentation slide with text/diagrams

These will be documented here when their corresponding scenarios are implemented.
