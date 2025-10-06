# Zk-Chat Observability Features

This document describes all of the observability features and hooks available in the zk-chat project. These features help developers and users understand system behavior, diagnose issues, and monitor performance.

## Table of Contents

1. [Logging Infrastructure](#logging-infrastructure)
2. [Progress Tracking](#progress-tracking)
3. [Metrics and Analytics](#metrics-and-analytics)
4. [Console Output and Theming](#console-output-and-theming)
5. [Service Provider Observability](#service-provider-observability)
6. [Plugin Observability Hooks](#plugin-observability-hooks)
7. [Git Integration Observability](#git-integration-observability)
8. [Configuration and Environment](#configuration-and-environment)
9. [Future Enhancements](#future-enhancements)

---

## Logging Infrastructure

Zk-chat uses [structlog](https://www.structlog.org/) for structured logging throughout the application, providing consistent, context-rich log messages.

### Logger Initialization

All modules initialize a logger at the module level:

```python
import structlog

logger = structlog.get_logger()
```

### Log Levels

The application uses standard Python logging levels configured via `logging.basicConfig()`:

- **WARN** (default): Standard operational mode
- **INFO**: Detailed operational information
- **DEBUG**: Detailed diagnostic information
- **ERROR**: Critical issues requiring attention

Configuration example:
```python
logging.basicConfig(level=logging.WARN)
```

### Structured Context

Structlog enables rich contextual information in log messages:

```python
logger.info(
    "Generated summary",
    document_path=document_path,
    original_length=len(content),
    summary_length=len(summary)
)
```

### Key Logging Locations

**Services**: 23+ files use logging including:
- `zk_chat/services/link_traversal_service.py` - Link analysis operations
- `zk_chat/services/service_provider.py` - Service discovery
- `zk_chat/services/service_registry.py` - Service registration
- `zk_chat/progress_tracker.py` - Progress tracking operations

**Tools**: 28+ logger calls across tool implementations:
- Document operations (create, read, update, delete)
- Git operations (commit, status)
- Link analysis and traversal
- Memory operations

**Core Components**: 128+ total logger invocations across the codebase

### Common Log Patterns

**Service Registration**:
```python
logger.info("Registered service", service_type=service_type.value)
```

**Warning Conditions**:
```python
logger.warning("Service not available", service_type=service_type.value)
```

**Error Handling**:
```python
logger.error("Tool execution failed", 
            tool_name=tool_name, 
            error=str(e))
```

**Task Completion**:
```python
logger.info("Task completed", user_request=problem, result=result)
```

---

## Progress Tracking

Zk-chat provides a rich progress tracking system using the [Rich](https://rich.readthedocs.io/) library for visual feedback during long-running operations.

### ProgressTracker Class

Located in `zk_chat/progress_tracker.py`, this class provides comprehensive progress tracking capabilities.

#### Features

- **Visual Progress Bars**: Shows completion percentage, elapsed time, and estimated time remaining
- **File-level Updates**: Displays current file being processed
- **Callback Support**: Enables progress updates from nested operations
- **Context Manager Support**: Automatic cleanup with `with` statements

#### Basic Usage

```python
from zk_chat.progress_tracker import ProgressTracker

with ProgressTracker() as tracker:
    tracker.start_progress("Processing documents", total=100)
    
    for i, file in enumerate(files):
        # Process file...
        tracker.update_progress(
            advance=1,
            current_file=file
        )
```

#### Progress Callback Pattern

Many operations support optional progress callbacks:

```python
# Type definition
ProgressCallback = Callable[[str, int, int], None]

# Usage in Zettelkasten operations
def index_documents_for_document_search(
    self,
    progress_callback: Optional[ProgressCallback] = None
) -> None:
    """
    Index documents with optional progress updates.
    
    Args:
        progress_callback: Optional callback for progress updates 
                          (filename, processed_count, total_count)
    """
    # ...
    if progress_callback:
        progress_callback(relative_path, i + 1, total_files)
```

#### IndexingProgressTracker

Specialized progress tracker for document indexing operations:

```python
tracker = IndexingProgressTracker()

# Scanning phase (indeterminate)
tracker.start_scanning("Scanning vault for markdown files...")

# Processing phase (determinate)
tracker.finish_scanning(file_count)

# Update during processing
tracker.update_file_processing(filename, processed_count)
```

#### Progress Display Columns

The progress tracker displays:
- **Spinner**: Visual indicator of activity
- **Description**: Current operation description
- **Current File**: File being processed (fixed width, truncated if needed)
- **Progress Bar**: Visual completion indicator
- **Count**: "X of Y" completion counter
- **Percentage**: Completion percentage
- **Time Elapsed**: Time since operation started
- **Time Remaining**: Estimated time to completion

---

## Metrics and Analytics

Zk-chat provides built-in metrics for analyzing the structure and health of your Zettelkasten.

### Link Metrics

The `LinkTraversalService` provides comprehensive link graph metrics through the `get_link_metrics()` method.

#### LinkMetrics Model

```python
class LinkMetrics(BaseModel):
    """Metrics about the link graph structure."""
    total_documents: int
    total_links: int
    total_resolved_links: int
    total_broken_links: int
    orphaned_documents: List[str]  # documents with no incoming links
    hub_documents: List[Tuple[str, int]]  # documents with most incoming links
    average_links_per_document: float
    link_density: float  # ratio of actual links to possible links
```

#### Global Metrics

Get metrics for the entire vault:

```python
metrics = link_service.get_link_metrics()

print(f"Total Documents: {metrics.total_documents}")
print(f"Total Links: {metrics.total_links}")
print(f"Broken Links: {metrics.total_broken_links}")
print(f"Orphaned Documents: {len(metrics.orphaned_documents)}")
print(f"Average Links per Document: {metrics.average_links_per_document:.2f}")
print(f"Link Density: {metrics.link_density:.4f}")
print(f"Top Hub Documents: {metrics.hub_documents[:5]}")
```

#### Document-Specific Metrics

Get metrics for a single document:

```python
metrics = link_service.get_link_metrics(document="My Document.md")

print(f"Forward Links: {metrics.total_links}")
print(f"Backward Links: {metrics.hub_documents[0][1]}")
print(f"Broken Links: {metrics.total_broken_links}")
print(f"Is Orphaned: {document in metrics.orphaned_documents}")
```

### Vault Health Analysis

The agent prompt (`zk_chat/agent_prompt.txt`) describes a vault health reporting feature:

**Vault-Health Report** (weekly/on request):
- Orphaned notes (no incoming links)
- Isolated clusters (disconnected subgraphs)
- Over-central hubs (documents with too many links)
- Missing metadata
- Broken wikilinks

Reports are saved to `/reports/vault-health-<date>.md`.

### Index Statistics

While not yet fully exposed, the architecture supports index statistics:

```python
# Proposed IndexStats structure (from COMPOSITIONAL_ARCHITECTURE.md)
class IndexStats:
    total_documents: int
    total_excerpts: int
    last_updated: datetime
```

---

## Console Output and Theming

Zk-chat provides a consistent, themed console experience using the Rich library.

### RichConsoleService

Located in `zk_chat/console_service.py`, this service provides themed console output.

#### Theme Configuration

```python
theme = Theme({
    "banner.title": "bold bright_cyan",
    "banner.copyright": "bright_blue", 
    "banner.info.label": "white",
    "banner.info.value": "green",
    "banner.warning.unsafe": "bold bright_red",
    "banner.warning.git": "yellow",
    "chat.user": "bold blue",
    "chat.assistant": "green",
    "chat.system": "dim yellow",
    "tool.info": "dim cyan",
})
```

#### Usage

```python
from zk_chat.console_service import RichConsoleService

console_service = RichConsoleService()

# Themed output
console_service.print("[tool.info]Processing document...[/]")
console_service.print("[banner.warning.unsafe]Warning: Unsafe mode enabled[/]")

# User input
response = console_service.input("Enter your query: ")

# Direct console access
console = console_service.get_console()
```

#### Print Statements

The codebase contains 119+ `print()` statements for direct user feedback, following the convention:
- Use `logger` for diagnostic/operational messages
- Use `print()` (or RichConsoleService) for direct user feedback

---

## Service Provider Observability

The service provider pattern includes built-in observability for service discovery and availability.

### Service Registration Logging

When services are registered:

```python
self._logger.info("Registered service", service_type=service_type.value)
```

### Service Availability Checks

```python
def has_service(self, service_type: ServiceType) -> bool:
    """Check if a service is available."""
    available = self._service_provider.has_service(service_type)
    if not available:
        logger.warning("Service not available", service_type=service_type.value)
    return available
```

### Service Types

Available services that can be monitored:
- `FILESYSTEM_GATEWAY`
- `LLM_BROKER`
- `ZETTELKASTEN`
- `SMART_MEMORY`
- `CHROMA_GATEWAY`
- `MODEL_GATEWAY`
- `TOKENIZER_GATEWAY`
- `GIT_GATEWAY` (optional)
- `CONFIG`

### Plugin Service Access

Plugins can check service availability:

```python
class MyPlugin(ZkChatPlugin):
    def run(self, input_text: str) -> str:
        if not self.has_service(ServiceType.GIT_GATEWAY):
            return "Git integration not available"
        
        git = self.require_service(ServiceType.GIT_GATEWAY)
        # Use git service...
```

---

## Plugin Observability Hooks

Plugins can leverage all observability features available in the zk-chat runtime.

### Structured Logging in Plugins

From `PLUGINS.md`:

```python
import structlog

logger = structlog.get_logger()

class MyPlugin(ZkChatPlugin):
    def run(self, input_text: str) -> str:
        logger.info(
            "Generated summary",
            document_path=document_path,
            original_length=len(content),
            summary_length=len(summary)
        )
        return result
```

### Service Provider Access

Plugins have full access to service provider observability:

```python
def run(self, input_text: str) -> str:
    # Check service availability
    if not self.has_service(ServiceType.ZETTELKASTEN):
        logger.warning("Zettelkasten service not available")
        return "Service unavailable"
    
    # Get service with logging
    zk = self.zettelkasten
    logger.info("Accessing Zettelkasten service")
```

### Plugin Registration

Plugins are registered with logging in the MCP server:

```python
def _register_tool(self, tool_instance: Any) -> None:
    descriptor = tool_instance.descriptor
    if "function" in descriptor:
        tool_name = descriptor["function"]["name"]
        self.tools[tool_name] = tool_instance
        logger.info("Registered tool", name=tool_name)
```

### Error Handling

```python
try:
    result = self.process_document(document)
    logger.info("Document processed", document=document, result=result)
    return result
except Exception as e:
    logger.error("Processing failed", document=document, error=str(e))
    raise
```

---

## Git Integration Observability

Git operations include comprehensive observability for tracking version control activities.

### Commit Changes Logging

From `zk_chat/tools/commit_changes.py`:

```python
try:
    # Operations...
    success, commit_output = self.git.commit(commit_message)
    if not success:
        return f"Error committing changes: {commit_output}"
    
    return f"Successfully committed changes: '{commit_message}'"
except Exception as e:
    logger.error("Unexpected error", error=str(e))
    return f"Unexpected error committing changes: {str(e)}"
```

### Git Operations

The `GitGateway` class provides observability for:
- **Status checks**: View uncommitted changes
- **Diff generation**: See changes before committing
- **Commit operations**: Track commit success/failure
- **Add operations**: Track file staging

### Agent Commit Strategy

From `zk_chat/agent_prompt.txt`, the agent follows this observable commit strategy:

1. `get_uncommitted_changes` → review
2. Craft concise commit message
3. `commit_changes`

This provides a clear audit trail of changes.

---

## Configuration and Environment

### Environment Variables

**OPENAI_API_KEY**: OpenAI API key (required when using OpenAI gateway)
```python
if not os.environ.get("OPENAI_API_KEY"):
    # Error: OpenAI API key required
```

**CHROMA_TELEMETRY**: ChromaDB telemetry control (set to 'false' throughout the app)
```python
os.environ['CHROMA_TELEMETRY'] = 'false'
```

### Configuration Logging

Configuration changes and access are logged:

```python
config = self.config
logger.info("Vault configuration", vault=config.vault, model=config.model)
```

### Global Configuration

Stored in `~/.zk_chat`:
- Bookmarks (vault paths)
- Last opened vault
- Persistent user preferences

Operations on global config can be monitored:

```python
def add_bookmark(self, vault_path: str) -> None:
    """Add a bookmark with the given vault path."""
    abs_path = os.path.abspath(vault_path)
    self.bookmarks.add(abs_path)
    self.save()
    logger.info("Added bookmark", vault_path=abs_path)
```

---

## Future Enhancements

Based on the `COMPOSITIONAL_ARCHITECTURE.md` document and current state, potential observability enhancements include:

### Index Statistics

Expose comprehensive index statistics:

```python
class IndexStats:
    total_documents: int
    total_excerpts: int
    last_updated: datetime
    average_document_length: int
    index_size_bytes: int
```

### Performance Metrics

Add timing and performance tracking:
- Document indexing rate (docs/second)
- Query response times
- Embedding generation times
- Link traversal performance

### Event Hooks

Provide event hooks for external monitoring:

```python
class ZkEventListener:
    def on_document_indexed(self, document: str, duration: float) -> None: ...
    def on_query_completed(self, query: str, results: int, duration: float) -> None: ...
    def on_link_updated(self, document: str, links_added: int, links_removed: int) -> None: ...
```

### Metrics Export

Support for external monitoring systems:
- Prometheus metrics endpoint
- StatsD integration
- CloudWatch metrics
- Custom metric backends

### Audit Logging

Enhanced audit trail:
- All document modifications
- Query patterns
- User actions
- Configuration changes

### Health Checks

Standardized health check endpoints:
- Vector database connectivity
- LLM gateway availability
- Index freshness
- Git repository status

### Dashboard Integration

Real-time monitoring dashboard showing:
- Active operations and progress
- Recent errors and warnings
- Link graph statistics
- Index health metrics
- System resource usage

---

## Best Practices

### For Plugin Developers

1. **Use structured logging**: Include relevant context in all log messages
2. **Check service availability**: Use `has_service()` before accessing services
3. **Handle errors gracefully**: Log errors with context before propagating
4. **Provide progress feedback**: Use progress callbacks for long operations
5. **Document observable behavior**: Describe what gets logged and when

### For Application Developers

1. **Configure appropriate log levels**: WARN for production, INFO/DEBUG for development
2. **Monitor service registration**: Watch for service availability issues
3. **Track progress on long operations**: Use ProgressTracker for user feedback
4. **Analyze link metrics regularly**: Identify vault health issues
5. **Review commit messages**: Ensure Git integration provides clear audit trail

### For Users

1. **Check console output**: Themed messages provide operational context
2. **Review vault health reports**: Identify structural issues
3. **Monitor progress bars**: Understand operation status
4. **Examine log files**: Diagnose issues when things go wrong
5. **Use git log**: Review document change history

---

## Related Documentation

- [PLUGINS.md](PLUGINS.md) - Plugin development guide with logging examples
- [COMPOSITIONAL_ARCHITECTURE.md](COMPOSITIONAL_ARCHITECTURE.md) - Architectural design including proposed metrics
- [.junie/guidelines.md](.junie/guidelines.md) - Logging conventions and best practices
- [README.md](README.md) - General usage and features

---

## Summary

Zk-chat provides a comprehensive observability framework including:

✅ **Structured logging** with 128+ log points across the codebase
✅ **Rich progress tracking** with visual feedback and callbacks
✅ **Link graph metrics** for vault health analysis
✅ **Themed console output** for consistent user experience
✅ **Service provider observability** for monitoring dependencies
✅ **Plugin observability hooks** for extensibility
✅ **Git integration tracking** for audit trails
✅ **Configuration and environment** monitoring

This foundation enables developers and users to understand system behavior, diagnose issues, and monitor the health of their Zettelkasten.
