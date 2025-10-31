## Lead Qualification Sequential Agent

### Overview

This example demonstrates a simple, production-like sequential workflow for qualifying sales leads. A top-level sequential agent orchestrates three specialized sub-agents in a fixed order: validate the lead, score the lead, then recommend the next action. It uses a minimal callback approach that initializes state once at the beginning of the run.

### Quickstart

- Entry point: import the root agent and hand it to your ADK runner.

```python
from sequential_agent.lead_agent.agent import root_agent

# Example invocation in an ADK-compatible runtime:
# response = run_agent(root_agent, user_input={"lead": "..."})
# print(response)
```

### What It Does

1. Validates that a lead contains enough information for qualification.
2. Assigns a 1–10 score with a concise justification.
3. Recommends concrete next actions for sales based on validation and score.

### How It Works

- The top-level `SequentialAgent` named `LeadQualificationPipeline` defines an ordered list of sub-agents.
- Each sub-agent is an `LlmAgent` with a clear instruction and an `output_key` that writes results back into the shared run state.
- Later sub-agents consume earlier outputs by referencing those `output_key` values in their prompts (e.g., `{validation_status}`, `{lead_score}`).
- A minimal callback pattern initializes run state once before execution; no per-step callbacks are required.

### Architecture

- `lead_agent/agent.py`
  - Creates the `SequentialAgent` with sub-agents in order:
    - `LeadValidatorAgent` → `LeadScorerAgent` → `ActionRecommenderAgent`
- `lead_agent/subagents/validator/agent.py`
  - Validates lead completeness; outputs `validation_status` as either `valid` or `invalid: reason`.
- `lead_agent/subagents/scorer/agent.py`
  - Scores the lead 1–10 with a one-sentence justification; outputs `lead_score`.
- `lead_agent/subagents/recommender/agent.py`
  - Produces next-step recommendations conditioned on `validation_status` and `lead_score`; outputs `action_recommendation`.

### Execution Flow

```
User input → SequentialAgent (init once) →
  LeadValidatorAgent → writes validation_status →
  LeadScorerAgent    → writes lead_score        →
  ActionRecommender  → uses both to recommend   →
Final response
```

### Using Sequential Agents Effectively

- Ordering matters: place sub-agents so that downstream steps have the inputs they need.
- Chain via `output_key`: each `LlmAgent` should write a single, well-named key. Reference it in later prompts using `{your_key}`.
- Keep outputs structured: constrain each sub-agent to a compact format (e.g., numeric score, single token `valid/invalid`), which reduces ambiguity for downstream steps.
- Minimal callback: if you only need initial state, prefer a single before-run initialization over per-step hooks.
- Fail-fast validation: ensure the first step validates inputs so later steps don’t produce misleading results.
- Deterministic prompts: be explicit in examples and formatting so later steps can reliably parse earlier outputs.

### Notes

- Default model shown: `gemini-2.0-flash`. Replace with your available model as needed.
- This example focuses on control flow and shared state passing, not on external tools.


