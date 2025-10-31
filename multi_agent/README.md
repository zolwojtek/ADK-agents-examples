## Manager Multi-Agent (Delegation Example)

### Overview

This example shows a manager agent that delegates user requests to specialized sub-agents and also calls certain agents as tools. It demonstrates three patterns at once:
- Direct sub-agent delegation (`it_agent`, `stock_agent`)
- Tool usage (`get_current_time`)
- Wrapping an agent as a tool (`news_agent` via `AgentTool`)

### Quickstart

Import the root manager agent and run it in your ADK runtime:

```python
from multi_agent.manager_agent.agent import root_agent

# response = run_agent(root_agent, user_input={"request": "What's new in AI today?"})
```

### What It Does

- Routes jokes/IT banter to `it_agent` (which uses a `get_nerd_joke` tool).
- Routes stock requests to `stock_agent` (which uses `get_stock_price`).
- Can fetch current time via `get_current_time` tool.
- Calls `news_agent` as a tool for news queries (web search + summarize), without fully delegating control.

### How It Works

- `manager_agent/agent.py` defines `root_agent` with:
  - Sub-agents: `it_agent`, `stock_agent`
  - Tools: `get_current_time` and `AgentTool(news_agent)`
- `news_agent` is a full `Agent` that uses `google_search` internally, but is exposed to the manager as a callable tool using `AgentTool`. This lets the manager stay in control of the overall conversation while leveraging the news agent’s expertise in a single call.

### Architecture

- `manager_agent/agent.py`: Manager composition and instruction for delegation + tools.
- `manager_agent/sub_agents/it_agent/agent.py`: IT jokes agent with `get_nerd_joke` tool (updates state with `last_joke_topic`).
- `manager_agent/sub_agents/stock_agent/agent.py`: Stock prices agent using `yfinance` through `get_stock_price`.
- `manager_agent/sub_agents/news_agent/agent.py`: News analysis agent using `google_search`.
- `manager_agent/tools/tools.py`: `get_current_time` utility tool.

### Execution Flow

```
User request → Manager Agent →
  - If IT/joke → delegate to it_agent (tool-backed)
  - If stocks → delegate to stock_agent (tool-backed)
  - If news → call AgentTool(news_agent) as a tool
  - Else → handle directly or request clarification
```

### When to Wrap an Agent as a Tool (AgentTool)

Use `AgentTool(sub_agent)` instead of adding the sub-agent to `sub_agents` when:
- You need a single, synchronous call for a narrowly scoped task, and the manager should retain turn-level control.
- The sub-task is best modeled as a function-like capability (input → result), rather than a delegated multi-turn sub-conversation.
- You want to standardize results into tool-return shapes (e.g., for logging, retries, observability).
- You need to apply tool-level governance (timeouts, rate limits, guardrails) to an agent’s behavior.

Prefer adding a sub-agent to `sub_agents` when:
- The task benefits from a delegated, potentially multi-turn interaction where the sub-agent drives the mini-conversation.
- The sub-agent must maintain its own internal context for several steps before handing control back.

### Practical Notes

- Models: examples use `gemini-2.0-flash` or `gemini-2.5-flash`. Swap for available models.
- External deps: `yfinance` for stocks; `google_search` tool for news.
- State: tools can read/write session state via tool context (e.g., `last_joke_topic`).


