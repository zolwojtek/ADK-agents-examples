## Parallel System Agent

### Overview

This example demonstrates using a `ParallelAgent` to collect system information concurrently (CPU, Memory, Disk) and then a `SequentialAgent` to synthesize a single report. It showcases how to combine parallel fan-out (independent work in sub-agents) with a sequential fan-in (final synthesis).

### Quickstart

- Import the root agent and hand it to your ADK runtime:

```python
from parallel_agent.system_agent.agent import root_agent

# Example with your runner
# response = run_agent(root_agent, user_input={"request": "System health report"})
```

### What It Does

1. Gathers CPU, memory, and disk data in parallel using tool-backed `LlmAgent`s.
2. Waits for all three to complete.
3. Synthesizes a comprehensive, markdown-formatted system report.

### How It Works

- `system_agent/agent.py` defines:
  - `system_info_gatherer`: a `ParallelAgent` with three sub-agents:
    - `CpuInfoAgent` (uses `get_cpu_info`)
    - `MemoryInfoAgent` (uses `get_memory_info`)
    - `DiskInfoAgent` (uses `get_disk_info`)
  - `root_agent`: a `SequentialAgent` that runs `system_info_gatherer` first, then `SystemReportSynthesizer`.
- Each info agent writes its output to the shared state via `output_key` (`cpu_info`, `memory_info`, `disk_info`).
- The synthesizer references those keys in its prompt to compose the final report.

### Files

- `system_agent/agent.py`: Composes the parallel gatherer and sequential synthesizer pipeline.
- `system_agent/subagents/*_info_agent/agent.py`: Tool-backed `LlmAgent`s for CPU/Memory/Disk.
- `system_agent/subagents/*_info_agent/tools.py`: `psutil`-based system information tools.
- `system_agent/subagents/synthesizer_agent/agent.py`: Merges partial reports into a final system health report.

### Execution Flow

```
User request → Sequential(root) → Parallel(gatherers: CPU, Memory, Disk) →
Wait for all → Synthesizer uses {cpu_info}, {memory_info}, {disk_info} → Report
```

### When to Use a Parallel Agent

- Independent subtasks: Multiple steps that don’t depend on each other’s intermediate outputs (e.g., fetching metrics from different services).
- Latency reduction: You need aggregate results fast; parallelization cuts end-to-end time.
- Fan-out/fan-in patterns: Gather many inputs then merge into a single output (e.g., multi-source search, multi-modal analysis).
- Tool or API calls in parallel: Sub-agents call separate tools or services, each with their own latency or rate limits.
- Ensemble approaches: Run several specialized analyzers and combine their conclusions.

### Practical Tips

- Keep sub-agent outputs small and well-structured. Use `output_key` names that are clear and stable.
- Make each sub-agent deterministic and tool-grounded; avoid hallucination by requiring tool calls where applicable.
- Ensure the synthesizer’s prompt explicitly references each `output_key` and gives a target format.
- Bound parallelism: A `ParallelAgent` is best for a modest number of independent tasks; consider batching for very large fan-outs.

### Requirements

- The info tools use `psutil`. Ensure it is available in your environment.
- Default models in the example use `gemini-2.0-flash`; swap to any available model if needed.


