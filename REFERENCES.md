# Document References in Chat History

## Overview

This document outlines the design for incorporating document references into the chat history system. When users reference documents via wikilinks or when the assistant retrieves documents through search, these references should be tracked, displayed to users, and made available to the LLM in a structured way.

## Problem Statement

Currently, the chat system doesn't explicitly track or display which documents are being referenced in conversations. This creates several issues:

1. Users can't easily see which documents influenced an assistant's response
2. Wikilinks in user messages are not processed or tracked
3. Documents found via search tools are not explicitly linked to the responses they inform
4. There's no persistent record of document-to-conversation relationships
5. The LLM doesn't receive explicit prompting to use referenced documents

## Goals

1. **Extract and track wikilinks** from user messages
2. **Track documents** used by the assistant via search tools
3. **Display references** to users in a clear, consistent format
4. **Provide references to the LLM** in a way that encourages their use
5. **Maintain backward compatibility** with existing chat sessions
6. **Support document summarization** for enhanced reference display

## Design Components

### 1. Data Model Extensions

#### 1.1 Message Reference Structure

We need to extend the message data model to include document references. Since we're using the `mojentic` library's `LLMMessage` class, we'll track references separately but associate them with messages.

```python
from typing import List, Optional
from pydantic import BaseModel

class DocumentReference(BaseModel):
    """
    Represents a reference to a document in the vault.
    
    This can be either a direct reference (from a wikilink) or an indirect
    reference (from a search result that informed the response).
    """
    wikilink: str  # The original wikilink, e.g., "[[parameters reference]]"
    relative_path: Optional[str]  # Resolved path, None if broken link
    reference_type: str  # "direct" (from wikilink) or "search" (from tool result)
    summary: Optional[str] = None  # Optional AI-generated summary
    context_snippet: Optional[str] = None  # Optional context from the source

class MessageReferences(BaseModel):
    """
    Contains all document references associated with a message.
    """
    message_index: int  # Index in the chat session's messages list
    references: List[DocumentReference]
    
class ChatSessionMetadata(BaseModel):
    """
    Metadata tracked alongside a ChatSession to support enhanced features.
    """
    message_references: List[MessageReferences] = []
```

#### 1.2 Integration with ChatSession

Since `ChatSession` is from the `mojentic` library, we'll create a wrapper or companion class:

```python
class EnhancedChatSession:
    """
    Wraps mojentic.llm.ChatSession with additional reference tracking.
    """
    def __init__(self, chat_session: ChatSession):
        self.chat_session = chat_session
        self.metadata = ChatSessionMetadata()
        self.wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        
    def send_with_references(self, query: str) -> tuple[str, List[DocumentReference]]:
        """
        Send a query, extract references, and return both response and references.
        """
        # Extract wikilinks from user query
        user_refs = self._extract_wikilinks_from_query(query)
        
        # Augment query with reference prompts if needed
        augmented_query = self._augment_query_with_references(query, user_refs)
        
        # Send to LLM
        response = self.chat_session.send(augmented_query)
        
        # Track user message references
        user_msg_idx = len(self.chat_session.messages) - 2  # -1 is assistant, -2 is user
        if user_refs:
            self.metadata.message_references.append(
                MessageReferences(message_index=user_msg_idx, references=user_refs)
            )
        
        # Extract assistant references (from tool calls)
        assistant_refs = self._extract_assistant_references()
        assistant_msg_idx = len(self.chat_session.messages) - 1
        if assistant_refs:
            self.metadata.message_references.append(
                MessageReferences(message_index=assistant_msg_idx, references=assistant_refs)
            )
        
        return response, assistant_refs
```

### 2. Wikilink Extraction and Processing

#### 2.1 User Message Processing

When a user sends a message with wikilinks:

```python
def _extract_wikilinks_from_query(self, query: str) -> List[DocumentReference]:
    """
    Extract wikilinks from user query and resolve them.
    
    Example query: "Can you explain [[parameters reference]] and [[tool usage]]?"
    Returns: [
        DocumentReference(wikilink="[[parameters reference]]", relative_path="docs/params.md", ...),
        DocumentReference(wikilink="[[tool usage]]", relative_path="docs/tools.md", ...)
    ]
    """
    references = []
    
    # Find all wikilinks
    matches = self.wikilink_pattern.finditer(query)
    
    for match in matches:
        wikilink_text = match.group(0)  # Full [[...]]
        link_title = match.group(1)      # Just the title
        
        # Resolve the wikilink
        try:
            relative_path = self.filesystem_gateway.resolve_wikilink(wikilink_text)
            
            # Create reference
            ref = DocumentReference(
                wikilink=wikilink_text,
                relative_path=relative_path,
                reference_type="direct",
                context_snippet=None  # Could extract surrounding text
            )
            references.append(ref)
            
        except ValueError:
            # Broken link
            ref = DocumentReference(
                wikilink=wikilink_text,
                relative_path=None,
                reference_type="direct",
                context_snippet="Warning: Document not found"
            )
            references.append(ref)
    
    return references
```

#### 2.2 Query Augmentation

Augment the user's query with reference information:

```python
def _augment_query_with_references(self, query: str, references: List[DocumentReference]) -> str:
    """
    Augment user query with structured reference information.
    
    Before: "Can you explain [[parameters reference]]?"
    
    After: "Can you explain [[parameters reference]]?
    
    Referenced Documents:
    - [[parameters reference]] (docs/params.md): A detailed reference for all parameters...
    
    Please read these documents using the read_zk_document tool if you need more information."
    """
    if not references:
        return query
    
    # Build reference list
    ref_lines = ["\n\nReferenced Documents:"]
    
    for ref in references:
        if ref.relative_path:
            # Optionally get summary
            summary = ref.summary or self._generate_summary(ref.relative_path)
            ref_lines.append(f"- {ref.wikilink} ({ref.relative_path}): {summary}")
        else:
            ref_lines.append(f"- {ref.wikilink}: Warning - Document not found")
    
    ref_lines.append("\nPlease read these documents using the read_zk_document tool if you need more information.")
    
    return query + "\n".join(ref_lines)
```

### 3. Assistant Reference Tracking

#### 3.1 Detecting Tool Usage

Track when the assistant uses document-retrieval tools:

```python
def _extract_assistant_references(self) -> List[DocumentReference]:
    """
    Extract document references from the assistant's recent tool calls.
    
    This monitors tool calls like:
    - read_zk_document
    - find_excerpts
    - find_zk_documents
    
    And creates DocumentReferences for documents that were accessed.
    """
    references = []
    
    # Get the most recent assistant message
    if not self.chat_session.messages:
        return references
    
    last_message = self.chat_session.messages[-1]
    
    # Check if message has tool calls
    if not last_message.tool_calls:
        return references
    
    for tool_call in last_message.tool_calls:
        tool_name = tool_call.function.name
        
        # Handle read_zk_document
        if tool_name == "read_zk_document":
            args = json.loads(tool_call.function.arguments)
            relative_path = args.get("relative_path")
            if relative_path:
                # Create wikilink from path
                wikilink = self._path_to_wikilink(relative_path)
                references.append(DocumentReference(
                    wikilink=wikilink,
                    relative_path=relative_path,
                    reference_type="search",
                    context_snippet="Retrieved via read_zk_document"
                ))
        
        # Handle find_excerpts
        elif tool_name == "find_excerpts":
            # Parse tool response to get document IDs
            # This requires access to tool results
            excerpts = self._parse_excerpt_results(tool_call)
            for excerpt in excerpts:
                doc_id = excerpt.get("document_id")
                if doc_id:
                    wikilink = self._path_to_wikilink(doc_id)
                    references.append(DocumentReference(
                        wikilink=wikilink,
                        relative_path=doc_id,
                        reference_type="search",
                        context_snippet=excerpt.get("text", "")[:100]
                    ))
        
        # Handle find_zk_documents_related_to
        elif tool_name == "find_zk_documents":
            documents = self._parse_document_results(tool_call)
            for doc in documents:
                relative_path = doc.get("relative_path")
                if relative_path:
                    wikilink = self._path_to_wikilink(relative_path)
                    references.append(DocumentReference(
                        wikilink=wikilink,
                        relative_path=relative_path,
                        reference_type="search",
                        context_snippet="Found via semantic search"
                    ))
    
    # Deduplicate references
    unique_refs = {}
    for ref in references:
        if ref.relative_path not in unique_refs:
            unique_refs[ref.relative_path] = ref
    
    return list(unique_refs.values())
```

### 4. Document Summary Generation

#### 4.1 Summary Service

Create a service to generate concise document summaries:

```python
class DocumentSummaryService:
    """
    Generates concise summaries of documents for reference display.
    """
    def __init__(self, llm: LLMBroker, zettelkasten: Zettelkasten):
        self.llm = llm
        self.zk = zettelkasten
        self.cache = {}  # Simple in-memory cache
    
    def get_summary(self, relative_path: str, max_length: int = 100) -> str:
        """
        Get or generate a summary for a document.
        
        Uses a simple strategy:
        1. Check cache
        2. Try to use first paragraph of document
        3. If needed, use LLM to generate summary
        """
        # Check cache
        if relative_path in self.cache:
            return self.cache[relative_path]
        
        # Read document
        try:
            document = self.zk.read_document(relative_path)
        except Exception:
            return "Unable to access document"
        
        # Try first paragraph
        paragraphs = document.content.split("\n\n")
        if paragraphs and len(paragraphs[0]) < max_length:
            summary = paragraphs[0].strip()
            self.cache[relative_path] = summary
            return summary
        
        # Generate with LLM
        prompt = f"Summarize this document in one sentence:\n\n{document.content[:1000]}"
        summary = self.llm.complete(prompt, max_tokens=50)
        
        self.cache[relative_path] = summary
        return summary
```

### 5. Reference Display

#### 5.1 Console Display

Display references to users in the console:

```python
class ConsoleReferenceRenderer:
    """
    Renders document references in the console output.
    """
    def __init__(self, console_service: RichConsoleService):
        self.console = console_service
    
    def render_references(self, references: List[DocumentReference]) -> None:
        """
        Display references in a readable format.
        
        Output example:
        
        📚 Referenced Documents:
        • [[parameters reference]] (docs/params.md)
          A detailed reference for all parameters you can send to the tool
        • [[tool usage]] (docs/tools.md)
          Guide for using available tools in the chat interface
        """
        if not references:
            return
        
        self.console.print("\n[bold cyan]📚 Referenced Documents:[/bold cyan]")
        
        for ref in references:
            if ref.relative_path:
                self.console.print(f"  • [link]{ref.wikilink}[/link] ({ref.relative_path})")
                if ref.summary:
                    self.console.print(f"    [dim]{ref.summary}[/dim]")
            else:
                self.console.print(f"  • [yellow]{ref.wikilink}[/yellow] [dim](not found)[/dim]")
        
        self.console.print("")
```

#### 5.2 GUI Display

For the Qt GUI, references could be displayed in a side panel or as expandable sections:

```python
class QtReferenceWidget(QWidget):
    """
    Widget to display document references in the GUI.
    """
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Referenced Documents")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)
        
        # List widget for references
        self.ref_list = QListWidget()
        self.ref_list.itemClicked.connect(self.on_reference_clicked)
        layout.addWidget(self.ref_list)
        
        self.setLayout(layout)
    
    def update_references(self, references: List[DocumentReference]):
        """Update the displayed references."""
        self.ref_list.clear()
        
        for ref in references:
            if ref.relative_path:
                item_text = f"{ref.wikilink}\n{ref.summary or ref.relative_path}"
            else:
                item_text = f"{ref.wikilink}\n(Document not found)"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, ref)
            self.ref_list.addItem(item)
    
    def on_reference_clicked(self, item):
        """Handle reference click - could open document in viewer."""
        ref = item.data(Qt.UserRole)
        if ref.relative_path:
            # Emit signal or trigger document viewer
            self.document_opened.emit(ref.relative_path)
```

### 6. Integration Points

#### 6.1 Chat Module Integration

Modify `zk_chat/chat.py`:

```python
def chat(config: Config, unsafe: bool = False, use_git: bool = False, store_prompt: bool = False):
    # ... existing setup code ...
    
    # Create base chat session
    chat_session = ChatSession(
        llm,
        system_prompt=system_prompt,
        tools=tools
    )
    
    # Wrap with enhanced session
    enhanced_session = EnhancedChatSession(
        chat_session=chat_session,
        filesystem_gateway=filesystem_gateway,
        zettelkasten=zk,
        llm=llm
    )
    
    # Reference renderer
    ref_renderer = ConsoleReferenceRenderer(console_service)
    
    while True:
        query = console_service.input("[chat.user]Query:[/] ")
        if not query:
            console_service.print("[chat.system]Exiting...[/]")
            break
        else:
            # Send with reference tracking
            response, assistant_refs = enhanced_session.send_with_references(query)
            
            # Display response
            console_service.print(f"[chat.assistant]{response}[/]")
            
            # Display references if any
            if assistant_refs:
                ref_renderer.render_references(assistant_refs)
```

#### 6.2 Agent Module Integration

Similar integration for `zk_chat/agent.py`:

```python
def agent(config: Config):
    # ... existing setup code ...
    
    # Wrap the problem-solving agent with reference tracking
    enhanced_agent = EnhancedIterativeProblemSolvingAgent(
        base_agent=problem_solver,
        filesystem_gateway=filesystem_gateway,
        zettelkasten=zk,
        llm=llm
    )
    
    # ... rest of agent code ...
```

### 7. Storage and Persistence

#### 7.1 Optional: Persist References

For advanced use cases, we might want to persist reference metadata:

```python
class ReferenceStore:
    """
    Optional: Store reference metadata persistently.
    """
    def __init__(self, vault_path: str):
        self.db_path = os.path.join(vault_path, ".zk_chat_db", "references.json")
    
    def save_session_references(self, session_id: str, metadata: ChatSessionMetadata):
        """Save references for a chat session."""
        # Load existing data
        data = self._load_data()
        
        # Update with new session
        data[session_id] = metadata.model_dump()
        
        # Save
        self._save_data(data)
    
    def get_session_references(self, session_id: str) -> Optional[ChatSessionMetadata]:
        """Retrieve references for a chat session."""
        data = self._load_data()
        session_data = data.get(session_id)
        
        if session_data:
            return ChatSessionMetadata.model_validate(session_data)
        return None
```

### 8. Implementation Phases

#### Phase 1: Core Infrastructure (Foundation)
- [ ] Create `DocumentReference` and `MessageReferences` models
- [ ] Create `EnhancedChatSession` wrapper class
- [ ] Implement wikilink extraction from user queries
- [ ] Add basic tests for reference extraction

#### Phase 2: Assistant Reference Tracking
- [ ] Implement tool call monitoring for `read_zk_document`
- [ ] Implement tool call monitoring for `find_excerpts`
- [ ] Implement tool call monitoring for `find_zk_documents_related_to`
- [ ] Add tests for reference detection from tool calls

#### Phase 3: Summary Generation
- [ ] Create `DocumentSummaryService`
- [ ] Implement first-paragraph summary extraction
- [ ] Implement LLM-based summary generation (optional)
- [ ] Add caching for summaries
- [ ] Add tests for summary service

#### Phase 4: Query Augmentation
- [ ] Implement query augmentation with reference prompts
- [ ] Add formatting for reference lists in prompts
- [ ] Test that LLM responds to reference prompts appropriately

#### Phase 5: Display Integration
- [ ] Create `ConsoleReferenceRenderer`
- [ ] Integrate with `chat.py` main loop
- [ ] Integrate with `agent.py` main loop
- [ ] Add tests for rendering

#### Phase 6: GUI Integration (Optional)
- [ ] Create `QtReferenceWidget`
- [ ] Integrate with Qt GUI
- [ ] Add reference click handling
- [ ] Add tests for GUI components

#### Phase 7: Persistence (Optional)
- [ ] Create `ReferenceStore` for persistent storage
- [ ] Integrate with session management
- [ ] Add tests for persistence

#### Phase 8: Polish and Documentation
- [ ] Add comprehensive documentation
- [ ] Create usage examples
- [ ] Update README with reference tracking features
- [ ] Add troubleshooting guide

## Technical Considerations

### 1. Performance

- **Summary Caching**: Cache document summaries to avoid repeated LLM calls
- **Lazy Loading**: Only generate summaries when needed for display
- **Reference Deduplication**: Avoid tracking the same document multiple times in one message

### 2. Error Handling

- **Broken Links**: Handle wikilinks that don't resolve gracefully
- **Tool Call Parsing**: Robust parsing of tool results to extract document references
- **Missing Documents**: Handle cases where referenced documents are deleted

### 3. Backward Compatibility

- **Optional Feature**: Reference tracking should be optional and not break existing code
- **Graceful Degradation**: If reference tracking fails, chat should continue normally
- **Existing Sessions**: Support for sessions without reference metadata

### 4. User Experience

- **Unobtrusive Display**: References should enhance, not clutter the interface
- **Actionable References**: Users should be able to click/navigate to referenced documents
- **Clear Feedback**: Make it clear when a wikilink is broken or a reference is unavailable

## Testing Strategy

### Unit Tests
- Test wikilink extraction from various message formats
- Test reference deduplication logic
- Test summary generation and caching
- Test tool call parsing for different tool types

### Integration Tests
- Test full flow: user query with wikilinks → augmented prompt → LLM response
- Test assistant reference detection from tool usage
- Test reference display in console
- Test reference display in GUI

### Edge Cases
- Empty messages
- Messages with only wikilinks
- Broken wikilinks
- Multiple references to same document
- Tool calls that return no results
- Large numbers of references (>10)

## Future Enhancements

1. **Reference Analytics**: Track which documents are most frequently referenced
2. **Smart Suggestions**: Suggest related documents based on conversation context
3. **Reference Graphs**: Visualize document relationships discovered through chat
4. **Export with References**: Export conversations with embedded reference metadata
5. **Cross-Session References**: Track document usage across multiple chat sessions
6. **Reference Highlighting**: Highlight referenced text in source documents

## Open Questions

1. Should we automatically read documents when they're wikilinked, or just prompt the LLM to do so?
2. How many references should we show before truncating the display?
3. Should document summaries be stored permanently or regenerated each time?
4. How should we handle references in multi-turn conversations?
5. Should we track negative references (documents that were searched but not used)?

## Dependencies

### Existing Components
- `mojentic.llm.ChatSession` - Base chat session
- `MarkdownFilesystemGateway` - Wikilink resolution
- `Zettelkasten` - Document access
- `RichConsoleService` - Console output
- `LLMBroker` - Summary generation

### New Components
- `DocumentReference` model
- `MessageReferences` model
- `EnhancedChatSession` wrapper
- `DocumentSummaryService`
- `ConsoleReferenceRenderer`
- `QtReferenceWidget` (optional)
- `ReferenceStore` (optional)

## Migration Path

Since this is a new feature with no existing data to migrate:

1. **Phase 1**: Implement as optional feature flag
2. **Phase 2**: Enable by default for new sessions
3. **Phase 3**: Remove feature flag once stable
4. **Phase 4**: Consider persistence for advanced users

## Success Criteria

1. Users can see which documents are referenced in their queries
2. Users can see which documents informed assistant responses
3. Document summaries provide helpful context without requiring clicks
4. Reference display doesn't clutter the chat interface
5. Feature works seamlessly in both CLI and GUI modes
6. All tests pass with >90% code coverage
7. Documentation is clear and includes examples
8. Performance impact is minimal (<100ms overhead per message)
