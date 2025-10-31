# ADK Crash Course

A comprehensive collection of examples demonstrating Google's Agent Development Kit (ADK) capabilities. Each example focuses on specific ADK features and patterns, with detailed README files explaining concepts, architecture, and best practices.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   - Create a `.env` file with your Google Cloud credentials
   - Configure `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` if using Vertex AI

3. **Explore examples:** Each directory contains a working example with its own README

## Examples Overview

### Basic Agents
- **`greeting_agent/`** - Minimal agent example showing the simplest ADK setup
- **`question_agent/`** - Basic agent with session state using instruction templates
- **`email_agent/`** - Structured output example using Pydantic models for JSON responses

### Tools
- **`tool_agent/`** - Demonstrates built-in vs custom tools and critical tool usage limitations

### Memory & Sessions
- **`memory_agent/`** - Persistent session state with SQLite database, managing reminders across conversations

### Agent Orchestration
- **`sequential_agent/`** - Lead qualification pipeline showing ordered sub-agent execution
- **`parallel_agent/`** - System monitoring example with concurrent information gathering
- **`loop_agent/`** - Iterative refinement pattern for content quality improvement
- **`multi_agent/`** - Manager agent with delegation and `AgentTool` wrapping

### Advanced Patterns
- **`callbacks/`** - Three examples demonstrating agent, model, and tool-level callbacks for intercepting execution
  - `before_after_agent/` - Request logging and timing
  - `before_after_model/` - Content filtering and response transformation
  - `before_after_tool/` - Tool argument modification and response enhancement
- **`stateful-multi-agent/`** - Enterprise-grade multi-agent system with domain-driven design, event sourcing, and projections

## Learning Path

**Start here if you're new:**
1. `greeting_agent/` - Understand basic agent structure
2. `question_agent/` - Learn about session state
3. `tool_agent/` - Master tool usage (important limitations)

**Then explore orchestration:**
4. `sequential_agent/` - Linear workflows
5. `parallel_agent/` - Concurrent operations
6. `loop_agent/` - Iterative refinement
7. `multi_agent/` - Delegation patterns

**Advanced topics:**
8. `callbacks/` - Execution interception and modification
9. `memory_agent/` - Persistent state management
10. `stateful-multi-agent/` - Complex system architecture

## Key Concepts Covered

- **Agent Types**: Basic `Agent`, `LlmAgent`, workflow agents (`SequentialAgent`, `ParallelAgent`, `LoopAgent`)
- **Tools**: Built-in tools vs custom tools, tool limitations, `AgentTool` wrapping
- **State Management**: Session state, persistent storage, state passing between agents
- **Structured Output**: Pydantic schemas for guaranteed response formats
- **Callbacks**: Hooks into agent, model, and tool execution
- **Multi-Agent Systems**: Delegation, sub-agents, agent hierarchies
- **Advanced Patterns**: Event-driven architecture, domain events, projections, DDD

## Requirements

- Python 3.8+
- Google ADK (`google-adk`)
- Google Cloud credentials (for Vertex AI models)
- See `requirements.txt` for full dependency list

## Documentation

Each example directory contains a detailed `README.md` explaining:
- What the example demonstrates
- How it works (architecture and execution flow)
- When to use the pattern
- Best practices and limitations
- Code structure and key files

## Additional Resources

- [ADK Official Documentation](https://google.github.io/adk-docs/)
- Each example's README contains specific references to relevant ADK documentation

