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

Instead of wrapping the `mojentic` library's ChatSession, we'll manage our own rich message structure within zk-chat. This gives us full control over the chat session data and allows us to maintain document references directly on messages for local UI purposes, while still converting to the simpler `LLMMessage` format when communicating with the LLM.

```python
from typing import List, Optional
from pydantic import BaseModel
from mojentic.llm.gateways.models import LLMMessage

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

class ZkChatMessage(BaseModel):
    """
    Rich message structure for zk-chat that includes document references.
    
    This is our internal representation that maintains all the context we need
    for UI display and reference tracking. We convert this to LLMMessage when
    sending to the LLM.
    """
    role: str  # "user", "assistant", or "system"
    content: str  # The message content
    references: List[DocumentReference] = []  # Documents referenced in this message
    timestamp: Optional[str] = None  # When the message was created
    tool_calls: Optional[List] = None  # Tool calls made (for assistant messages)
    
    # Token accounting for context management
    token_count: Optional[int] = None  # Tokens in the original message content
    augmented_token_count: Optional[int] = None  # Tokens after adding references/formatting
    tool_tokens: Optional[int] = None  # Tokens used by tool calls (for assistant messages)
    
    def to_llm_message(self) -> LLMMessage:
        """
        Convert our rich message to mojentic's simpler LLMMessage format.
        
        When converting, we may augment the content with reference information
        to provide context to the LLM.
        """
        from mojentic.llm.gateways.models import MessageRole
        
        content = self.content
        
        # For user messages with references, augment with reference list
        if self.role == "user" and self.references:
            ref_lines = ["\n\nReferenced Documents:"]
            for ref in self.references:
                if ref.relative_path:
                    summary = ref.summary or ""
                    ref_lines.append(f"- {ref.wikilink} ({ref.relative_path}): {summary}")
                else:
                    ref_lines.append(f"- {ref.wikilink}: Warning - Document not found")
            ref_lines.append("\nPlease read these documents using the read_zk_document tool if you need more information.")
            content = content + "\n".join(ref_lines)
        
        return LLMMessage(
            role=MessageRole[self.role.capitalize()],
            content=content,
            tool_calls=self.tool_calls
        )
```

#### 1.2 ZkChatSession - Our Own Chat Session Manager

Rather than wrapping `mojentic.llm.ChatSession`, we'll create our own chat session manager that maintains the rich message structure and handles conversion to/from the LLM:

```python
class ZkChatSession:
    """
    Manages a chat session with rich message structures and document reference tracking.
    
    This class maintains parallel arrays:
    - messages: List[ZkChatMessage] - Our rich internal messages with references
    - llm_session: ChatSession - The underlying mojentic chat session for LLM communication
    
    The rich messages are used for local UI display and reference tracking,
    while the LLM session manages the actual conversation with the model.
    
    Token Accounting:
    The session tracks token usage for all components to enable context optimization:
    - Individual message token counts
    - Tool description token overhead
    - Tool request/response token usage
    - Total context budget management
    """
    def __init__(
        self,
        llm: LLMBroker,
        system_prompt: str,
        tools: List[LLMTool],
        filesystem_gateway: MarkdownFilesystemGateway,
        zettelkasten: Zettelkasten,
        tokenizer_gateway: TokenizerGateway,
        max_context: int = 32768,
        temperature: float = 1.0,
        # Context budget allocation (as percentages of max_context)
        message_budget_ratio: float = 0.6,  # 60% for conversation messages
        tool_budget_ratio: float = 0.3,     # 30% for tool descriptions/calls
        system_budget_ratio: float = 0.1    # 10% for system prompt
    ):
        # Our rich message history
        self.messages: List[ZkChatMessage] = []
        
        # Underlying LLM session (from mojentic)
        self.llm_session = ChatSession(
            llm=llm,
            system_prompt=system_prompt,
            tools=tools,
            max_context=max_context,
            temperature=temperature
        )
        
        # Dependencies for reference tracking
        self.filesystem_gateway = filesystem_gateway
        self.zettelkasten = zettelkasten
        self.tokenizer_gateway = tokenizer_gateway
        self.wikilink_pattern = re.compile(r'\[\[([^\]]+)\]\]')
        
        # Context management
        self.max_context = max_context
        self.message_budget = int(max_context * message_budget_ratio)
        self.tool_budget = int(max_context * tool_budget_ratio)
        self.system_budget = int(max_context * system_budget_ratio)
        
        # Token tracking
        self.system_prompt_tokens = self._count_tokens(system_prompt)
        self.tool_description_tokens = self._calculate_tool_tokens(tools)
        self.current_message_tokens = 0
        
    def send(self, user_message: str) -> tuple[str, ZkChatMessage, ZkChatMessage]:
        """
        Send a user message and return the assistant's response.
        
        Returns:
            tuple[str, ZkChatMessage, ZkChatMessage]: 
                - The response text (for backward compatibility)
                - The user message (with references)
                - The assistant message (with references)
        """
        # Extract references from user message
        user_refs = self._extract_wikilinks_from_message(user_message)
        
        # Calculate token counts for user message
        user_token_count = self._count_tokens(user_message)
        
        # Create rich user message
        user_msg = ZkChatMessage(
            role="user",
            content=user_message,
            references=user_refs,
            timestamp=datetime.now().isoformat(),
            token_count=user_token_count
        )
        
        # Convert to LLM message and calculate augmented token count
        llm_message = user_msg.to_llm_message()
        user_msg.augmented_token_count = self._count_tokens(llm_message.content)
        
        # Add to our message history
        self.messages.append(user_msg)
        
        # Send to LLM
        response_text = self.llm_session.send(llm_message.content)
        
        # Extract references from assistant's tool usage
        assistant_refs = self._extract_assistant_references()
        
        # Calculate token counts for assistant message
        assistant_token_count = self._count_tokens(response_text)
        tool_calls = self._get_recent_tool_calls()
        tool_token_count = self._calculate_tool_call_tokens(tool_calls) if tool_calls else 0
        
        # Create rich assistant message
        assistant_msg = ZkChatMessage(
            role="assistant",
            content=response_text,
            references=assistant_refs,
            timestamp=datetime.now().isoformat(),
            tool_calls=tool_calls,
            token_count=assistant_token_count,
            tool_tokens=tool_token_count
        )
        
        # Add to our message history
        self.messages.append(assistant_msg)
        
        return response_text, user_msg, assistant_msg
    
    def get_messages(self) -> List[ZkChatMessage]:
        """Get all messages with their references for UI display."""
        return self.messages
    
    def get_llm_messages(self) -> List[LLMMessage]:
        """Get simplified messages for LLM context (if needed for debugging)."""
        return [msg.to_llm_message() for msg in self.messages]
    
    def _count_tokens(self, text: str) -> int:
        """Count tokens in a text string using the tokenizer gateway."""
        return self.tokenizer_gateway.count_tokens(text)
    
    def _calculate_tool_tokens(self, tools: List[LLMTool]) -> int:
        """Calculate total tokens used by tool descriptions."""
        total = 0
        for tool in tools:
            descriptor_text = json.dumps(tool.descriptor)
            total += self._count_tokens(descriptor_text)
        return total
    
    def get_context_usage(self) -> dict:
        """
        Get detailed breakdown of context token usage.
        
        Returns:
            dict with keys:
                - system_tokens: Tokens used by system prompt
                - tool_tokens: Tokens used by tool descriptions
                - message_tokens: Tokens used by conversation messages
                - total_tokens: Total tokens in context
                - available_tokens: Remaining tokens before max_context
                - budget_status: Usage vs allocated budgets
        """
        message_tokens = sum(
            (msg.augmented_token_count or msg.token_count or 0) 
            for msg in self.messages
        )
        
        total_tokens = (
            self.system_prompt_tokens + 
            self.tool_description_tokens + 
            message_tokens
        )
        
        return {
            "system_tokens": self.system_prompt_tokens,
            "tool_tokens": self.tool_description_tokens,
            "message_tokens": message_tokens,
            "total_tokens": total_tokens,
            "available_tokens": self.max_context - total_tokens,
            "budget_status": {
                "system": {
                    "used": self.system_prompt_tokens,
                    "budget": self.system_budget,
                    "percentage": (self.system_prompt_tokens / self.system_budget * 100) if self.system_budget > 0 else 0
                },
                "tools": {
                    "used": self.tool_description_tokens,
                    "budget": self.tool_budget,
                    "percentage": (self.tool_description_tokens / self.tool_budget * 100) if self.tool_budget > 0 else 0
                },
                "messages": {
                    "used": message_tokens,
                    "budget": self.message_budget,
                    "percentage": (message_tokens / self.message_budget * 100) if self.message_budget > 0 else 0
                }
            }
        }
    
    def _calculate_tool_call_tokens(self, tool_calls: List) -> int:
        """Calculate tokens used by tool calls (requests and responses)."""
        if not tool_calls:
            return 0
        
        total = 0
        for call in tool_calls:
            # Tool call request
            if hasattr(call, 'function'):
                total += self._count_tokens(call.function.name)
                total += self._count_tokens(call.function.arguments)
            
            # Tool call response (if available)
            # This would need to be tracked from the actual tool execution
        
        return total
    
    def should_compact_context(self) -> bool:
        """
        Determine if context should be compacted based on budget usage.
        
        Returns True if message budget is exceeded or total usage is near max_context.
        """
        usage = self.get_context_usage()
        
        # Compact if message budget exceeded
        if usage["message_tokens"] > self.message_budget:
            return True
        
        # Compact if total usage is above 90% of max_context
        if usage["total_tokens"] > (self.max_context * 0.9):
            return True
        
        return False
```

### 2. Wikilink Extraction and Processing

#### 2.1 User Message Processing

When a user sends a message with wikilinks, the `ZkChatSession` extracts and resolves them:

```python
def _extract_wikilinks_from_message(self, message: str) -> List[DocumentReference]:
    """
    Extract wikilinks from user message and resolve them.
    
    Example message: "Can you explain [[parameters reference]] and [[tool usage]]?"
    Returns: [
        DocumentReference(wikilink="[[parameters reference]]", relative_path="docs/params.md", ...),
        DocumentReference(wikilink="[[tool usage]]", relative_path="docs/tools.md", ...)
    ]
    """
    references = []
    
    # Find all wikilinks
    matches = self.wikilink_pattern.finditer(message)
    
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

The references are stored directly on the `ZkChatMessage` object and are automatically formatted when converting to an LLM message via the `to_llm_message()` method shown in section 1.1.

### 3. Assistant Reference Tracking

#### 3.1 Detecting Tool Usage

Track when the assistant uses document-retrieval tools. This method is part of `ZkChatSession`:

```python
def _extract_assistant_references(self) -> List[DocumentReference]:
    """
    Extract document references from the assistant's recent tool calls.
    
    This monitors tool calls from the underlying LLM session like:
    - read_zk_document
    - find_excerpts
    - find_zk_documents
    
    And creates DocumentReferences for documents that were accessed.
    """
    references = []
    
    # Get the most recent messages from the LLM session
    if not self.llm_session.messages:
        return references
    
    last_message = self.llm_session.messages[-1]
    
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

### 4.2 Context Management and Adaptive Strategies

Managing context token budgets is critical for optimal LLM performance. The `ZkChatSession` provides mechanisms for tracking and adapting to context constraints.

#### 4.2.1 Token Budget Allocation

The session divides the total context window into budgets for different components:

```python
# Example budget allocation for 32K context window:
# - System prompt: 10% (~3.2K tokens) - Instructions for the LLM
# - Tool descriptions: 30% (~9.6K tokens) - Available tools and their schemas
# - Messages: 60% (~19.2K tokens) - Conversation history

# These ratios are configurable per session
chat_session = ZkChatSession(
    # ... other params ...
    max_context=32768,
    message_budget_ratio=0.6,
    tool_budget_ratio=0.3,
    system_budget_ratio=0.1
)
```

#### 4.2.2 Context Usage Monitoring

Track real-time context usage:

```python
# Get detailed context breakdown
usage = chat_session.get_context_usage()

print(f"System prompt: {usage['system_tokens']} tokens")
print(f"Tool descriptions: {usage['tool_tokens']} tokens")
print(f"Messages: {usage['message_tokens']} tokens")
print(f"Total: {usage['total_tokens']} / {chat_session.max_context}")
print(f"Available: {usage['available_tokens']} tokens")

# Check budget status for each component
for component, status in usage['budget_status'].items():
    print(f"{component}: {status['used']}/{status['budget']} ({status['percentage']:.1f}%)")
```

#### 4.2.3 Adaptive Context Management Strategies

When context budgets are exceeded, several strategies can be employed:

**Strategy 1: Message Compaction via Summarization**
```python
def compact_message_history(self, target_token_count: int) -> None:
    """
    Compact older messages by summarizing them to fit within target token count.
    
    Keeps recent messages intact for context continuity while summarizing
    older exchanges to reduce token usage.
    """
    if not self.should_compact_context():
        return
    
    # Keep the most recent N messages intact
    recent_message_count = 3  # Configurable
    messages_to_compact = self.messages[:-recent_message_count]
    recent_messages = self.messages[-recent_message_count:]
    
    # Summarize older messages
    summary_prompt = "Summarize the following conversation, preserving key information:\n\n"
    for msg in messages_to_compact:
        summary_prompt += f"{msg.role}: {msg.content}\n"
    
    summary = self.llm_session.llm.complete(summary_prompt, max_tokens=500)
    
    # Replace old messages with summary
    summary_msg = ZkChatMessage(
        role="system",
        content=f"[Previous conversation summary]: {summary}",
        timestamp=datetime.now().isoformat(),
        token_count=self._count_tokens(summary)
    )
    
    self.messages = [summary_msg] + recent_messages
```

**Strategy 2: Tool-Use vs Context Injection**

Adapt between including document content in context vs prompting tool usage:

```python
def should_inject_document_content(self, doc_size_tokens: int) -> bool:
    """
    Decide whether to inject document content into context or prompt tool usage.
    
    If message budget has room, inject content directly for faster access.
    If budget is tight, prompt LLM to use read_zk_document tool instead.
    """
    usage = self.get_context_usage()
    available_budget = self.message_budget - usage['message_tokens']
    
    # Use 20% of available budget as threshold
    threshold = available_budget * 0.2
    
    if doc_size_tokens < threshold:
        return True  # Inject content directly
    else:
        return False  # Prompt tool usage
```

**Strategy 3: Dynamic Tool Filtering**

Reduce tool description overhead by filtering to relevant tools:

```python
def filter_tools_by_relevance(self, user_message: str, tools: List[LLMTool]) -> List[LLMTool]:
    """
    Filter tools to only include those relevant to the current query.
    
    Reduces tool_tokens overhead by excluding tools unlikely to be used.
    """
    # Use simple keyword matching or embeddings for tool relevance
    relevant_tools = []
    
    # Always include core navigation tools
    core_tool_names = {"read_zk_document", "find_excerpts", "resolve_wikilink"}
    
    for tool in tools:
        tool_name = tool.descriptor["function"]["name"]
        
        # Include core tools
        if tool_name in core_tool_names:
            relevant_tools.append(tool)
            continue
        
        # Include if keywords match
        tool_desc = tool.descriptor["function"]["description"].lower()
        if any(keyword in user_message.lower() for keyword in tool_desc.split()[:5]):
            relevant_tools.append(tool)
    
    return relevant_tools if relevant_tools else tools  # Fallback to all tools
```

**Strategy 4: Reference Storage in Smart Memory**

For frequently referenced documents, store references in smart memory:

```python
def store_document_reference_in_memory(self, doc_ref: DocumentReference) -> None:
    """
    Store document reference in smart memory for future retrieval.
    
    Instead of re-injecting full document content, LLM can retrieve
    the reference from memory on demand.
    """
    memory_entry = {
        "type": "document_reference",
        "wikilink": doc_ref.wikilink,
        "path": doc_ref.relative_path,
        "summary": doc_ref.summary,
        "last_accessed": datetime.now().isoformat()
    }
    
    # Store in smart memory with appropriate metadata
    self.smart_memory.store(
        content=json.dumps(memory_entry),
        metadata={"type": "reference", "path": doc_ref.relative_path}
    )
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

Modify `zk_chat/chat.py` to use our new `ZkChatSession`:

```python
def chat(config: Config, unsafe: bool = False, use_git: bool = False, store_prompt: bool = False):
    # ... existing setup code for llm, zk, filesystem_gateway, tools ...
    
    # Create our rich chat session instead of mojentic's ChatSession directly
    chat_session = ZkChatSession(
        llm=llm,
        system_prompt=system_prompt,
        tools=tools,
        filesystem_gateway=filesystem_gateway,
        zettelkasten=zk,
        max_context=32768,
        temperature=1.0
    )
    
    # Reference renderer for displaying references
    ref_renderer = ConsoleReferenceRenderer(console_service)
    
    while True:
        query = console_service.input("[chat.user]Query:[/] ")
        if not query:
            console_service.print("[chat.system]Exiting...[/]")
            break
        else:
            # Send message - returns response text and both messages with references
            response, user_msg, assistant_msg = chat_session.send(query)
            
            # Display response
            console_service.print(f"[chat.assistant]{response}[/]")
            
            # Display references if any were used by the assistant
            if assistant_msg.references:
                ref_renderer.render_references(assistant_msg.references)
            
            # Optionally, also show user references if they were resolved
            # (could be shown inline or as a separate section)
```

#### 6.2 Agent Module Integration

Similar integration for `zk_chat/agent.py`:

```python
def agent(config: Config):
    # ... existing setup code ...
    
    # Create ZkChatSession for the agent instead of basic ChatSession
    chat_session = ZkChatSession(
        llm=llm,
        system_prompt=system_prompt,
        tools=tools,
        filesystem_gateway=filesystem_gateway,
        zettelkasten=zk
    )
    
    # The agent can now access rich message history with references
    problem_solver = IterativeProblemSolvingAgent(
        chat_session=chat_session,  # Pass our rich session
        # ... other parameters ...
    )
    
    # ... rest of agent code ...
```

#### 6.3 GUI Integration

For the Qt GUI, we can access the full message history with references:

```python
class ChatWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.chat_session = None  # Will be ZkChatSession
        self.ref_widget = QtReferenceWidget()
        
    def send_message(self, user_text: str):
        """Send a message and update the UI."""
        # Send and get rich messages back
        response, user_msg, assistant_msg = self.chat_session.send(user_text)
        
        # Display messages in chat history
        self.add_message_to_ui(user_msg)
        self.add_message_to_ui(assistant_msg)
        
        # Update reference widget with assistant references
        if assistant_msg.references:
            self.ref_widget.update_references(assistant_msg.references)
    
    def add_message_to_ui(self, message: ZkChatMessage):
        """Add a message with its references to the UI."""
        # Display message content
        self.chat_display.append_message(message.role, message.content)
        
        # Optionally display inline references
        if message.references:
            ref_summary = ", ".join([ref.wikilink for ref in message.references])
            self.chat_display.append_metadata(f"📚 References: {ref_summary}")
```

### 7. Storage and Persistence

#### 7.1 Optional: Persist Chat Sessions

For advanced use cases, we can persist entire chat sessions with references:

```python
class ChatSessionStore:
    """
    Optional: Store chat sessions with their rich message history.
    """
    def __init__(self, vault_path: str):
        self.db_path = os.path.join(vault_path, ".zk_chat_db", "chat_sessions.json")
    
    def save_session(self, session_id: str, chat_session: ZkChatSession):
        """Save a chat session with all its messages and references."""
        # Load existing data
        data = self._load_data()
        
        # Convert messages to serializable format
        messages_data = [msg.model_dump() for msg in chat_session.messages]
        
        # Update with new session
        data[session_id] = {
            "messages": messages_data,
            "created_at": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat()
        }
        
        # Save
        self._save_data(data)
    
    def load_session(self, session_id: str) -> Optional[List[ZkChatMessage]]:
        """Retrieve a chat session's message history."""
        data = self._load_data()
        session_data = data.get(session_id)
        
        if session_data:
            messages = [ZkChatMessage.model_validate(msg) for msg in session_data["messages"]]
            return messages
        return None
    
    def _load_data(self) -> dict:
        """Load session data from disk."""
        if os.path.exists(self.db_path):
            with open(self.db_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_data(self, data: dict):
        """Save session data to disk."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
```

### 8. Implementation Phases

#### Phase 1: Core Infrastructure (Foundation)
- [ ] Create `DocumentReference` model in `zk_chat/models.py`
- [ ] Create `ZkChatMessage` model with references array and token accounting fields
- [ ] Create `ZkChatSession` class to manage rich message history
- [ ] Add `TokenizerGateway` integration for token counting
- [ ] Implement budget allocation system (message/tool/system ratios)
- [ ] Implement wikilink extraction from user messages
- [ ] Add basic tests for reference extraction
- [ ] Add tests for token counting and budget tracking

#### Phase 2: Assistant Reference Tracking
- [ ] Implement tool call monitoring for `read_zk_document`
- [ ] Implement tool call monitoring for `find_excerpts`
- [ ] Implement tool call monitoring for `find_zk_documents_related_to`
- [ ] Add tool call token counting
- [ ] Add tests for reference detection from tool calls

#### Phase 3: Summary Generation
- [ ] Create `DocumentSummaryService`
- [ ] Implement first-paragraph summary extraction
- [ ] Implement LLM-based summary generation (optional)
- [ ] Add caching for summaries
- [ ] Add tests for summary service

#### Phase 4: Message Augmentation and Token Tracking
- [ ] Implement `ZkChatMessage.to_llm_message()` conversion with reference formatting
- [ ] Calculate and store token counts for original and augmented messages
- [ ] Test that reference lists are properly appended to LLM messages
- [ ] Test that LLM responds appropriately to reference prompts
- [ ] Validate token count accuracy

#### Phase 5: Context Management
- [ ] Implement `get_context_usage()` for real-time monitoring
- [ ] Implement `should_compact_context()` decision logic
- [ ] Add context compaction via message summarization
- [ ] Implement adaptive tool filtering
- [ ] Implement content injection vs tool-use decision making
- [ ] Add tests for all context management strategies

#### Phase 6: Display Integration
- [ ] Create `ConsoleReferenceRenderer`
- [ ] Integrate with `chat.py` main loop
- [ ] Integrate with `agent.py` main loop
- [ ] Add optional context usage display in UI
- [ ] Add tests for rendering

#### Phase 7: GUI Integration (Optional)
- [ ] Create `QtReferenceWidget`
- [ ] Integrate with Qt GUI
- [ ] Add reference click handling
- [ ] Add context usage visualization
- [ ] Add tests for GUI components

#### Phase 8: Persistence (Optional)
- [ ] Create `ChatSessionStore` for persistent storage of sessions
- [ ] Implement save/load for `ZkChatSession` with token data
- [ ] Add tests for persistence

#### Phase 9: Polish and Documentation
- [ ] Add comprehensive documentation
- [ ] Create usage examples for token management
- [ ] Update README with reference tracking and context management features
- [ ] Add troubleshooting guide for context issues

## Technical Considerations

### 1. Performance

- **Summary Caching**: Cache document summaries to avoid repeated LLM calls
- **Lazy Loading**: Only generate summaries when needed for display
- **Reference Deduplication**: Avoid tracking the same document multiple times in one message
- **Token Counting**: Use efficient tokenizer for accurate token accounting without performance penalties

### 2. Token Accounting and Context Management

- **Real-time Tracking**: Track token usage for every message and tool call
- **Budget Allocation**: Configurable budgets for system prompt, tools, and messages
- **Context Monitoring**: Real-time visibility into context usage and budget status
- **Automatic Compaction**: Trigger context compaction when budgets are exceeded
- **Adaptive Strategies**: 
  - Message summarization for older conversations
  - Tool filtering based on relevance
  - Dynamic choice between content injection vs tool usage
  - Smart memory integration for frequently referenced documents

### 3. Error Handling

- **Broken Links**: Handle wikilinks that don't resolve gracefully
- **Tool Call Parsing**: Robust parsing of tool results to extract document references
- **Missing Documents**: Handle cases where referenced documents are deleted
- **Token Calculation Failures**: Fallback to character-based estimation if tokenizer fails

### 4. Backward Compatibility

- **Optional Feature**: Reference tracking should be optional and not break existing code
- **Graceful Degradation**: If reference tracking fails, chat should continue normally
- **Existing Sessions**: Support for sessions without reference metadata
- **Token Fields Optional**: Token accounting fields are optional to support legacy messages

### 5. User Experience

- **Unobtrusive Display**: References should enhance, not clutter the interface
- **Actionable References**: Users should be able to click/navigate to referenced documents
- **Clear Feedback**: Make it clear when a wikilink is broken or a reference is unavailable
- **Context Visibility**: Optionally display context usage to help users understand token limits

## Testing Strategy

### Unit Tests
- Test wikilink extraction from various message formats
- Test reference deduplication logic
- Test summary generation and caching
- Test tool call parsing for different tool types
- Test token counting for messages, tools, and references
- Test budget allocation and tracking
- Test context usage calculation
- Test should_compact_context() decision logic

### Integration Tests
- Test full flow: user query with wikilinks → augmented prompt → LLM response
- Test assistant reference detection from tool usage
- Test reference display in console
- Test reference display in GUI
- Test token accounting across multi-turn conversations
- Test context compaction when budgets are exceeded
- Test adaptive tool filtering based on relevance
- Test content injection vs tool-use decision making

### Edge Cases
- Empty messages
- Messages with only wikilinks
- Broken wikilinks
- Multiple references to same document
- Tool calls that return no results
- Large numbers of references (>10)
- Messages that exceed token budgets
- Sessions approaching max_context limit
- Tool descriptions that change dynamically

## Future Enhancements

1. **Reference Analytics**: Track which documents are most frequently referenced
2. **Smart Suggestions**: Suggest related documents based on conversation context
3. **Reference Graphs**: Visualize document relationships discovered through chat
4. **Export with References**: Export conversations with embedded reference metadata
5. **Cross-Session References**: Track document usage across multiple chat sessions
6. **Reference Highlighting**: Highlight referenced text in source documents
7. **Advanced Context Management**:
   - Machine learning-based context prioritization
   - Automatic identification of key messages for preservation
   - Dynamic budget reallocation based on conversation patterns
   - Predictive tool loading based on conversation context
8. **Performance Optimization**:
   - Incremental token counting (cache and update deltas)
   - Parallel tokenization for large messages
   - Token estimation fallbacks for speed-critical paths
9. **Multi-Model Support**:
   - Per-model token counting strategies
   - Model-specific context window optimization
   - Adaptive strategies based on model capabilities

## Open Questions

1. Should we automatically read documents when they're wikilinked, or just prompt the LLM to do so?
2. How many references should we show before truncating the display?
3. Should document summaries be stored permanently or regenerated each time?
4. How should we handle references in multi-turn conversations?
5. Should we track negative references (documents that were searched but not used)?
6. **Token Budget Allocation**: What are the optimal default ratios for system/tool/message budgets across different use cases?
7. **Compaction Triggers**: At what budget usage percentage should we trigger automatic compaction?
8. **Compaction Strategy**: Should we use summarization, pruning, or a hybrid approach for context compaction?
9. **Tool Filtering**: How aggressive should tool filtering be? Should it be user-configurable?
10. **Token Estimation**: For models without native tokenizers, what estimation heuristics work best?

## Dependencies

### Existing Components
- `mojentic.llm.ChatSession` - Underlying LLM communication (we'll use internally)
- `mojentic.llm.gateways.models.LLMMessage` - Simple message format for LLM
- `mojentic.llm.gateways.tokenizer_gateway.TokenizerGateway` - Token counting for context management
- `MarkdownFilesystemGateway` - Wikilink resolution
- `Zettelkasten` - Document access
- `RichConsoleService` - Console output
- `LLMBroker` - Summary generation and LLM interaction
- `SmartMemory` - Reference storage and retrieval

### New Components
- `DocumentReference` model - Represents a document reference with metadata
- `ZkChatMessage` model - Rich message with references array and token accounting
- `ZkChatSession` class - Manages chat with rich message history and context budgets
- `DocumentSummaryService` - Generates document summaries
- `ConsoleReferenceRenderer` - Displays references in console
- `QtReferenceWidget` (optional) - GUI reference display
- `ChatSessionStore` (optional) - Persistent storage for chat sessions

### Token Accounting Dependencies
- Token counting integrated into every message
- Budget allocation system for context components
- Context usage monitoring and reporting
- Adaptive strategies for context management

## Migration Path

Since this is a new feature with no existing data to migrate:

1. **Phase 1**: Implement core `ZkChatSession` alongside existing `ChatSession` usage
2. **Phase 2**: Migrate `chat.py` to use `ZkChatSession`
3. **Phase 3**: Migrate `agent.py` to use `ZkChatSession`
4. **Phase 4**: Migrate GUI to use `ZkChatSession`
5. **Phase 5**: Remove old `ChatSession` direct usage once all modules migrated
6. **Phase 6**: Consider persistence for advanced users

## Success Criteria

1. Users can see which documents are referenced in their queries
2. Users can see which documents informed assistant responses
3. Document summaries provide helpful context without requiring clicks
4. Reference display doesn't clutter the chat interface
5. Feature works seamlessly in both CLI and GUI modes
6. All tests pass with >90% code coverage
7. Documentation is clear and includes examples
8. Performance impact is minimal (<100ms overhead per message)
9. **Token accounting accurately tracks context usage** across all components
10. **Budget allocation prevents context overflow** and maintains optimal LLM performance
11. **Context compaction strategies effectively manage long conversations** without losing critical information
12. **Adaptive strategies (tool filtering, content injection decisions)** improve context efficiency
13. **Users can monitor context usage** and understand when compaction occurs
14. **Token counting overhead is negligible** (<10ms per message)
