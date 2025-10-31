## Memory Agent (Persistent Reminders)

### Overview

This example demonstrates a single `Agent` with persistent session state backed by a SQLite database. The agent can remember a user's name and manage reminders across conversations using tool functions that read/write the session state.

### Quickstart

Run the interactive CLI demo:

```bash
python3 memory_agent/main.py
```

What it does:
- Uses `DatabaseSessionService` with `sqlite:///./my_agent_data.db` to persist sessions.
- Creates or resumes a session for a fixed `APP_NAME`/`USER_ID`.
- Starts a simple REPL; type messages like:
  - "My name is Alice"
  - "Add a reminder to buy milk"
  - "Show my reminders"
  - "Change my second reminder to pick up groceries"
  - "Delete the last reminder"
- Prints state before and after each turn.

### What It Does

- Remembers `user_name` and a list of `reminders` across runs.
- Supports add/view/update/delete reminders via tools.
- Applies smart reminder selection rules (first/last/ordinal, content matching, 1-based indices).

### How It Works

- `memory_agent/memory_agent/agent.py` defines the `memory_agent` with tools:
  - `add_reminder(reminder, tool_context)` → appends to `state["reminders"]`
  - `view_reminders(tool_context)` → returns current reminders
  - `update_reminder(index, updated_text, tool_context)` → edits item at 1-based `index`
  - `delete_reminder(index, tool_context)` → removes item at 1-based `index`
  - `update_user_name(name, tool_context)` → sets `state["user_name"]`
- The agent `instruction` encodes reminder management guidelines (indexing, matching by content, relative positions) and forbids clarifying which reminder—use best judgment or list when no match.
- `main.py` wires the agent into a `Runner` with `DatabaseSessionService` and provides a simple terminal loop.
- `utils.py` provides debugging helpers to print state and event details.

### Files

- `memory_agent/agent.py`: Agent definition and reminder tools.
- `main.py`: Interactive REPL with persistent sessions.
- `utils.py`: Helpers for state display and event inspection.
- `my_agent_data.db`: SQLite DB used by `DatabaseSessionService` (created/used locally).

### Execution Flow

```
Start → Load/Resume session → Prompt user → Run agent →
Tools update state (reminders/user_name) → Persist via DatabaseSessionService →
Show state before/after → Loop
```

### Usage Notes

- Persistence: Change the DB URL in `main.py` to point elsewhere (e.g., Postgres via SQLAlchemy-style URL) if supported by your environment.
- Indices are 1-based for user-facing operations; tools translate to 0-based for internal lists.
- If user asks to modify without an index, follow the content matching guidance in the instruction; otherwise list reminders and ask for specificity.
- Models: example uses `gemini-2.5-flash`; switch to an available model if needed.


