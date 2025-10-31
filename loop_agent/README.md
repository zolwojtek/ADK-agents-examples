## Loop Agent (Iterative Refinement)

### Overview

This example demonstrates a `LoopAgent` for iterative refinement: generating an initial LinkedIn post, then repeatedly reviewing and refining it until quality requirements are met. It showcases how to combine a `SequentialAgent` (generate then refine) with a `LoopAgent` that exits when a sub-agent explicitly calls `exit_loop`.

### Quickstart

Import the root agent and hand it to your ADK runtime:

```python
from loop_agent.linkedin_post_agent.agent import root_agent

# Example invocation
# response = run_agent(root_agent, user_input={"request": "Generate a LinkedIn post about ADK"})
```

### What It Does

1. Generates an initial LinkedIn post draft about an ADK tutorial.
2. Enters a refinement loop that:
   - Reviews the post for quality (length, content requirements, style).
   - If requirements are met → calls `exit_loop` to stop.
   - Otherwise → refines the post based on feedback.
   - Repeats up to `max_iterations=10`.
3. Returns the final refined post.

### How It Works

- `linkedin_post_agent/agent.py` defines:
  - `root_agent`: a `SequentialAgent` with:
    - `initial_post_generator` → creates first draft; outputs `current_post`.
    - `refinement_loop` → a `LoopAgent` with:
      - `post_reviewer` → evaluates quality; uses `count_characters` and `exit_loop` tools.
      - `post_refiner` → applies feedback; updates `current_post`.

### Architecture

- `linkedin_post_agent/agent.py`: Pipeline composition (sequential → loop).
- `linkedin_post_agent/subagents/post_generator/agent.py`: Creates the initial draft with content/style requirements; outputs `current_post`.
- `linkedin_post_agent/subagents/post_reviewer/agent.py`: Reviews `{current_post}`; validates length (1000-1500 chars), required elements, and style; outputs `review_feedback`; calls `exit_loop` when done.
- `linkedin_post_agent/subagents/post_reviewer/tools.py`: `count_characters` (validates length, updates `state["review_status"]`) and `exit_loop` (sets `tool_context.actions.escalate = True`).
- `linkedin_post_agent/subagents/post_refiner/agent.py`: Reads `{current_post}` and `{review_feedback}`; applies improvements; outputs `current_post` (updated).

### Execution Flow

```
User request → Sequential(root) →
  InitialPostGenerator → writes current_post →
  LoopAgent (max 10 iterations) →
    Iteration N:
      PostReviewer → checks quality →
        If meets requirements → exit_loop() → Loop exits
        Else → writes review_feedback →
      PostRefiner → reads current_post + review_feedback → updates current_post →
    Next iteration or exit
Final post
```

### Loop Exit Mechanism

- To exit a `LoopAgent`, a sub-agent must call a tool that sets `tool_context.actions.escalate = True` (e.g., `exit_loop`).
- The reviewer checks conditions (length, content, style). If all pass, it calls `exit_loop`, which triggers escalation and stops the loop.
- If `max_iterations` is reached without exit, the loop stops anyway.

### When to Use a Loop Agent

Use `LoopAgent` when you need iterative refinement or validation until a condition is met:

1. **Quality gates**: Refine content until it passes criteria (this example).
2. **Code generation**: Generate code, test it, fix issues, repeat until tests pass.
3. **Data validation**: Extract/parse data, validate format, correct errors, loop until valid.
4. **Plan-refine-execute**: Create a plan, review feasibility, adjust, repeat until executable.
5. **A/B refinement**: Generate variants, evaluate, pick best, refine further.
6. **Multi-step problem solving**: Break down a problem, solve steps, validate consistency, refine as needed.

Prefer a `SequentialAgent` when:
- Steps are linear and don't need iteration.
- Each step depends on the previous step's output in a one-pass flow.

Prefer a `ParallelAgent` when:
- All steps are independent and can run concurrently.
- You need to aggregate results but don't need iterative improvement.

### Best Practices

- Set a reasonable `max_iterations` (e.g., 5-10) to prevent infinite loops.
- Use clear exit conditions: encode them in the reviewer's instruction and tools.
- Make the exit condition deterministic when possible (e.g., length checks, format validation).
- Provide actionable feedback: the refiner needs specific guidance to improve.
- Update shared state consistently: use `output_key`s so the loop can read updated values.
- Guard against cycles: ensure each iteration makes progress toward the goal.

### Notes

- Default model: `gemini-2.0-flash`; swap to your available model if needed.
- The example uses `exit_loop` tool; you can use any tool that sets `escalate = True`.
- The `count_characters` tool also updates `state["review_status"]` for debugging/observability.

