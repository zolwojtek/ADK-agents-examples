## Callbacks (Hook into Agent Execution)

### Overview

This directory contains three examples demonstrating different types of callbacks in ADK. Callbacks allow you to intercept and modify behavior at different stages of agent execution: before/after the agent runs, before/after model calls, and before/after tool execution.

### Quickstart

Each example can be imported and used independently:

```python
# Agent-level callbacks
from callbacks.before_after_agent.agent import root_agent as agent_callback_example

# Model-level callbacks
from callbacks.before_after_model.agent import root_agent as model_callback_example

# Tool-level callbacks
from callbacks.before_after_tool.agent import root_agent as tool_callback_example
```

### Types of Callbacks

#### 1. Agent-Level Callbacks (`before_after_agent/`)

**When to Use:**
- Logging request/response cycles
- Measuring total execution time
- Initializing session state at the start of each agent invocation
- Cleanup or analytics after agent completion

**What They Do:**
- `before_agent_callback`: Runs once before the agent processes the user request
- `after_agent_callback`: Runs once after the agent completes processing

**Characteristics:**
- Execute at the outermost level (entire agent execution)
- Access to full session state
- Cannot modify the request/response content directly
- Best for observability and state management

**Example Usage:**
```python
def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    # Initialize counters, timestamps, etc.
    state = callback_context.state
    state["request_start_time"] = datetime.now()
    return None  # Continue normal processing

def after_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    # Calculate duration, log metrics, cleanup
    state = callback_context.state
    duration = (datetime.now() - state["request_start_time"]).total_seconds()
    print(f"Request took {duration:.2f} seconds")
    return None

root_agent = Agent(
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
)
```

#### 2. Model-Level Callbacks (`before_after_model/`)

**When to Use:**
- Content filtering (blocking inappropriate requests)
- Request/response transformation
- Logging model interactions
- Adding context or modifying prompts before the model sees them
- Post-processing model outputs (word replacements, formatting)

**What They Do:**
- `before_model_callback`: Runs before each LLM call; can block requests or modify the request
- `after_model_callback`: Runs after each LLM response; can modify or replace the response

**Characteristics:**
- Execute for every model call (including sub-agent calls)
- Can access and modify `LlmRequest`/`LlmResponse` objects
- Can short-circuit execution by returning an `LlmResponse` instead of `None`
- Best for content moderation and response transformation

**Example Usage:**
```python
def before_model_callback(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    # Check for inappropriate content
    if contains_inappropriate_content(llm_request):
        # Return early response, skip model call
        return LlmResponse(content=blocked_message)
    return None  # Continue with model call

def after_model_callback(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    # Modify response text
    modified_text = sanitize_response(llm_response)
    return LlmResponse(content=modified_text)  # Return modified response

root_agent = Agent(
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
)
```

#### 3. Tool-Level Callbacks (`before_after_tool/`)

**When to Use:**
- Modifying tool arguments before execution
- Blocking certain tool calls (security, rate limiting)
- Modifying tool responses after execution
- Adding metadata or logging to tool calls
- Implementing tool-level retries or error handling

**What They Do:**
- `before_tool_callback`: Runs before each tool execution; can modify arguments or skip the call
- `after_tool_callback`: Runs after each tool execution; can modify the tool's return value

**Characteristics:**
- Execute for every tool call
- Can access `tool`, `args`, `tool_context`, and `tool_response`
- Can modify arguments or return a custom response to bypass tool execution
- Best for tool-level governance and response transformation

**Example Usage:**
```python
def before_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext
) -> Optional[Dict]:
    # Normalize arguments
    if tool.name == "get_capital_city" and args.get("country") == "Merica":
        args["country"] = "United States"
    
    # Block restricted calls
    if args.get("country") == "restricted":
        return {"error": "Access denied"}  # Skip tool, return custom response
    
    return None  # Continue with tool execution

def after_tool_callback(
    tool: BaseTool, args: Dict[str, Any], tool_context: ToolContext, tool_response: Dict
) -> Optional[Dict]:
    # Modify response
    if "washington" in tool_response.get("result", "").lower():
        tool_response["result"] += " 🇺🇸"
        return tool_response
    
    return None  # Use original response

root_agent = Agent(
    tools=[get_capital_city],
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
)
```

### Callback Execution Order

When all three callback types are used, execution follows this order:

```
1. before_agent_callback
   └─ 2. before_model_callback (for first model call)
      └─ Model execution
      └─ 3. after_model_callback
         └─ 4. before_tool_callback (if tool is called)
            └─ Tool execution
            └─ 5. after_tool_callback
               └─ 6. before_model_callback (if agent calls model again)
                  └─ ... (repeat model/tool cycle)
└─ 7. after_agent_callback
```

### Decision Guide: Which Callback to Use?

| Use Case | Recommended Callback Type |
|----------|--------------------------|
| Logging total execution time | Agent-level |
| Request/response analytics | Agent-level |
| Initialize session state per request | Agent-level |
| Content filtering/blocking | Model-level |
| Transform model prompts | Model-level |
| Post-process model outputs | Model-level |
| Modify tool arguments | Tool-level |
| Block specific tool calls | Tool-level |
| Transform tool responses | Tool-level |
| Add metadata to tool calls | Tool-level |

### Best Practices

1. **Keep callbacks fast**: Don't block execution with slow operations (use async if needed).
2. **Return `None` to continue**: Return `None` unless you want to short-circuit execution.
3. **Handle errors gracefully**: Wrap callback logic in try/except to avoid breaking agent execution.
4. **Don't modify shared objects in place**: Use `copy.deepcopy()` when modifying request/response objects.
5. **Use appropriate level**: Agent-level for high-level observability, model-level for content, tool-level for tool governance.
6. **State management**: Agent-level callbacks are best for per-request state initialization.

### Limitations and Considerations

- **Model callbacks run for every model call**: Including calls made by sub-agents, which can create verbose logs.
- **Tool callbacks run for every tool call**: Consider performance when logging extensively.
- **Return values matter**: Returning a non-`None` value from a callback replaces the normal execution path.
- **Deep copying**: Always deep copy objects before modifying to avoid side effects.

### Examples

- **`before_after_agent/`**: Demonstrates request counting, timing, and state initialization
- **`before_after_model/`**: Shows content filtering (blocking "sucks") and word replacement ("problem" → "challenge")
- **`before_after_tool/`**: Illustrates argument normalization ("Merica" → "United States") and response enhancement (adding emoji)

### Reference

For more details on callbacks, see:
- [ADK Callbacks Documentation](https://google.github.io/adk-docs/callbacks/types-of-callbacks/)
- [Callback Patterns](https://google.github.io/adk-docs/callbacks/callback-patterns/)

