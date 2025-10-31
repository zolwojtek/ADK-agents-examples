## Tool Agent (Built-in vs Custom Tools)

### Overview

This example demonstrates using tools with an agent. It shows both a built-in tool (`google_search`) and a custom-defined tool (`get_current_time`), but only one can be active at a time due to ADK limitations. This example highlights critical rules about tool usage in ADK.

### Quickstart

Import the root agent and use it in your ADK runtime:

```python
from tool_agent.agent import root_agent

# Example invocation
# response = run_agent(root_agent, user_input={"query": "What's the latest news about AI?"})
```

### What It Does

- Shows an agent with `google_search` (built-in tool) enabled.
- Includes a commented-out custom tool (`get_current_time`) to demonstrate the limitation.
- Demonstrates the fundamental rule: **one built-in tool OR multiple custom tools, but not both together in a single agent**.

### How It Works

- `agent.py` defines:
  - `get_current_time`: A custom function tool that returns the current timestamp.
  - `google_search`: A built-in tool imported from `google.adk.tools`.
  - `root_agent`: Currently uses only `google_search` (the custom tool is commented out).

### Built-in vs Custom Tools

**Built-in Tools** (from `google.adk.tools`):
- Pre-configured tools provided by ADK (e.g., `google_search`, `BuiltInCodeExecutor`, `BigQueryTool`, etc.).
- See [ADK Built-in Tools documentation](https://google.github.io/adk-docs/tools/built-in-tools/) for the full list.
- Easy to use with minimal setup.
- Have strict limitations (see below).

**Custom Tools**:
- Function tools you define yourself (e.g., `get_current_time`, `calculate_total`, etc.).
- Created by defining Python functions with type hints.
- More flexible but require you to implement the logic.

### Critical Rules and Limitations

⚠️ **IMPORTANT**: These limitations are enforced by ADK and cannot be bypassed except where noted.

#### Rule 1: One Built-in Tool Per Agent

**For each root agent or single agent, only ONE built-in tool is supported. No other tools of any type can be used in the same agent.**

```python
# ❌ NOT SUPPORTED - Cannot mix built-in with custom tools
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    tools=[google_search, get_current_time],  # Mixing built-in + custom - NOT ALLOWED
)

# ❌ NOT SUPPORTED - Cannot use multiple built-in tools
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    code_executor=BuiltInCodeExecutor(),
    tools=[google_search],  # Built-in tool + code executor - NOT ALLOWED
)

# ✅ SUPPORTED - Only custom tools
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    tools=[get_current_time, another_custom_tool],  # Multiple custom tools - OK
)

# ✅ SUPPORTED - Only one built-in tool
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    tools=[google_search],  # Single built-in tool - OK
)
```

#### Rule 2: Built-in Tools in Sub-Agents

**Built-in tools cannot be used within sub-agents, with the exception of `GoogleSearchTool` and `VertexAiSearchTool` in ADK Python (using a workaround).**

```python
# ❌ NOT SUPPORTED - Built-in tool in sub-agent
coding_agent = Agent(
    name="CodeAgent",
    model="gemini-2.5-flash",
    code_executor=BuiltInCodeExecutor(),  # Built-in tool
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    sub_agents=[coding_agent],  # NOT ALLOWED
)

# ✅ SUPPORTED - Custom tools in sub-agents
custom_tool_agent = Agent(
    name="CustomAgent",
    model="gemini-2.5-flash",
    tools=[get_current_time],  # Custom tool - OK in sub-agent
)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    sub_agents=[custom_tool_agent],  # OK
)
```

### Workarounds

#### Using Multiple Built-in Tools or Combining with Custom Tools

To use multiple built-in tools or combine them with custom tools, wrap each specialized agent as a tool using `AgentTool`:

```python
from google.adk.tools.agent_tool import AgentTool
from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.code_executors import BuiltInCodeExecutor

# Create specialized agents, each with ONE built-in tool
search_agent = Agent(
    model='gemini-2.5-flash',
    name='SearchAgent',
    instruction="You're a specialist in Google Search",
    tools=[google_search],  # One built-in tool
)

coding_agent = Agent(
    model='gemini-2.5-flash',
    name='CodeAgent',
    instruction="You're a specialist in Code Execution",
    code_executor=BuiltInCodeExecutor(),  # One built-in executor
)

# Root agent wraps them as tools
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    description="Root Agent",
    tools=[AgentTool(agent=search_agent), AgentTool(agent=coding_agent)],  # Wrap as tools
)
```

#### Python-Only Workaround for Google Search and Vertex AI Search

In ADK Python, `GoogleSearchTool` and `VertexAiSearchTool` have a workaround that allows bypassing the multi-tools limit:

```python
from google.adk.tools import google_search

# Use bypass_multi_tools_limit=True (Python only)
root_agent = Agent(
    name="RootAgent",
    model="gemini-2.5-flash",
    tools=[google_search(bypass_multi_tools_limit=True), custom_tool],  # Workaround enabled
)
```

**Note**: This workaround only applies to `GoogleSearchTool` and `VertexAiSearchTool` in Python. It does not work for other built-in tools or in Java.

### Best Practices

1. **Prefer custom tools** when you need multiple tools in one agent.
2. **Use `AgentTool` wrapping** when you need multiple built-in tools or want to combine built-in and custom tools.
3. **Keep built-in tools at the root level** if possible (avoid sub-agents).
4. **Use the Python workaround** for `GoogleSearchTool` and `VertexAiSearchTool` only when necessary.
5. **Design agent hierarchies** strategically: root agent with custom tools, specialized sub-agents wrapped as `AgentTool` for built-in tools.

### Reference

For complete documentation on built-in tools and limitations, see:
- [ADK Built-in Tools Documentation](https://google.github.io/adk-docs/tools/built-in-tools/)
- [Use Built-in tools with other tools](https://google.github.io/adk-docs/tools/built-in-tools/#use-built-in-tools-with-other-tools)
