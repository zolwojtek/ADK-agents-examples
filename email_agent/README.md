## Email Agent (Structured Output Example)

### Overview

This example demonstrates an `LlmAgent` with **structured output** using Pydantic models. The agent generates professional emails and guarantees the response follows a specific JSON schema (`subject` and `body` fields) defined by a Pydantic `BaseModel`.

### Quickstart

Import the root agent and use it in your ADK runtime:

```python
from email_agent.agent import root_agent

# Example invocation
# response = run_agent(root_agent, user_input={"request": "Write an email to my manager about the project update"})
# The response will have a structured 'email' key with 'subject' and 'body' fields
```

### What It Does

- Generates professional, well-formatted emails based on user requests.
- Returns structured output with separate `subject` and `body` fields.
- Enforces output format using Pydantic schema validation.

### How It Works

- `agent.py` defines:
  - `EmailContent` (Pydantic `BaseModel`): Schema with `subject` and `body` fields.
  - `root_agent` (`LlmAgent`):
    - Uses `output_schema=EmailContent` to enforce structured JSON output.
    - Uses `output_key="email"` to store results in state under the `email` key.
    - Instruction includes guidelines for professional email writing and explicitly requires JSON format.

### Key Feature: Structured Output

This example showcases the `output_schema` parameter:
- **Guaranteed structure**: The model's response will always match the Pydantic schema.
- **Type safety**: Fields are typed (`str` with `Field` descriptions).
- **Validation**: Pydantic validates the output automatically.
- **Easy parsing**: Access structured fields directly (e.g., `response.email.subject`, `response.email.body`).

### Execution Flow

```
User request → EmailAgent → 
  Generates email following instruction guidelines →
  Formats output as JSON matching EmailContent schema →
  Validates via Pydantic →
  Stores in state["email"] →
  Returns structured response
```

### When to Use Structured Output

Use `output_schema` with Pydantic models when:
- **API responses**: You need consistent JSON shapes for downstream services.
- **Data extraction**: Parsing specific fields from unstructured text reliably.
- **Tool inputs**: Preparing inputs for functions that require specific types.
- **Validation**: Ensuring outputs meet format requirements (email addresses, dates, numbers, etc.).
- **Type safety**: Working in typed codebases that benefit from structured data.

### Best Practices

- Define clear field descriptions in `Field()` to guide the model.
- Keep schemas focused (2-5 fields work well; complex nested structures may reduce reliability).
- Mention the JSON format requirement in the instruction for better adherence.
- Use appropriate Pydantic validators if you need custom validation logic.

### Notes

- Default model: `gemini-2.5-flash`; swap to your available model if needed.
- The `output_key` ("email") makes the structured result available in session state for later reference.
- Pydantic is required; ensure it's installed in your environment.

