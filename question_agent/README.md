## Question Agent (Simple Example)

### Overview

This example shows the minimal building blocks of an agent powered conversation: a single `Agent` with a short instruction that can answer user questions while conditioning on simple session state (e.g., user name and preferences).

### Quickstart

- Run the included basic session demo:

```bash
python3 question_agent/basic_session.py
```

What it does:
- Creates an in-memory session with initial state (`user_name`, `user_preferences`).
- Instantiates a `Runner` with the `question_agent`.
- Sends a single user message (e.g., “What's John occupation?”).
- Streams events and prints the final response.
- Prints the final session state for inspection.

### What It Does

- Answers user questions using the configured model and instruction.
- Incorporates session state values into the prompt via `{user_name}` and `{user_preferences}`.

### How It Works

- `question_agent/question_agent/agent.py` defines a single `Agent` with:
  - `name`, `model`, `description`, and an `instruction` template that references session keys.
- `basic_session.py` demonstrates a minimal run loop:
  - Creates a session (via `InMemorySessionService`) with initial state.
  - Builds a `Runner` bound to `question_agent`.
  - Sends a user `types.Content` message and iterates streamed events.
  - On final response, prints the assistant's text.

### Files

- `question_agent/question_agent/agent.py`: Defines the `question_agent` instance.
- `question_agent/basic_session.py`: End-to-end runnable demo with a local session.

### Usage Notes

- Session State: Any keys in session state can be referenced inside `instruction` using `{key}` placeholders.
- Model: Default is `gemini-2.5-flash`; replace with an available model if needed.
- Persistence: The demo uses `InMemorySessionService`; for real apps, swap for a persistent session store.


