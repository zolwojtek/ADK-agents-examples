## Greeting Agent (Minimal Example)

### Overview

This is the simplest possible agent example - a single `Agent` with a basic greeting instruction. It demonstrates the minimal structure needed to create a working agent.

### Quickstart

Import the root agent and hand it to your ADK runtime:

```python
from greeting_agent import root_agent

# Example invocation
# response = run_agent(root_agent, user_input={"message": "Hello!"})
```

### What It Does

- Responds to user messages with helpful greetings and basic conversation.
- Uses the default model behavior with a simple instruction prompt.

### How It Works

- `agent.py` defines a single `Agent` with:
  - `name`: "greeting_agent"
  - `model`: "gemini-2.5-flash"
  - `description`: Simple description
  - `instruction`: Basic greeting instruction
  
- `__init__.py` includes optional Vertex AI initialization boilerplate (if using Vertex AI models).

### Files

- `agent.py`: The minimal agent definition (8 lines).
- `__init__.py`: Package initialization with optional Vertex AI setup.

### Notes

- This is the absolute minimum agent example - no tools, no sub-agents, no callbacks.
- Use this as a starting point to build more complex agents.
- Swap the model name if using a different model provider.
- If you need Vertex AI, ensure `GOOGLE_CLOUD_PROJECT` and `GOOGLE_CLOUD_LOCATION` are set in your environment.

