# Quickstart

This repository includes a runnable local demo that wires Application Services, AI agent tools, an Event Bus, and Read Model projections.

## Prerequisites
- Python 3.10+
- Project dependencies installed (see requirements.txt)

## Start the Agent (Local Demo)
Run the bootstrap script:

```bash
python3 stateful-multi-agent/agent_bootstrap.py
```

What happens:
- Composition root is built (in-memory repositories, EventBus, services, projections, AI handlers).
- Seed data is created via Application Services:
  - 1 policy ("Standard")
  - 2 courses ("Course A", "Course B")
  - 1 user (demo@example.com)
  - 1 order for Course A
- Events are emitted synchronously and projections update immediately.
- The script prints the seeded IDs.

Note: The bootstrap’s interactive loop currently echoes input (agent runtime placeholder). Integrate with your ADK chat runtime using the helper function below.

## Use with your ADK Agent Runtime
In your runner, import the agent and container:

```python
from agent_bootstrap import get_agent_container_and_seed
agent, container, ids = get_agent_container_and_seed()
# Hand `agent` to your ADK runtime. Tools will call application services internally.
```

The `CustomerServiceAgent` (LLM) will:
- Interpret user requests in natural language
- Invoke tools (e.g., list courses, create order, request refund)
- Tools call Application Services
- Services publish events → projections/handlers update

## Architecture Snapshot
- Event-driven updates: Services emit lightweight events (with `__event_type__`) to `EventBus`.
- Projections subscribe to relevant events via `ProjectionEventHandler` and update denormalized read models.
- AI handlers also subscribe to events for analytics/alerts.
- Tools (`stateful_multi_agent/tools.py`) wrap calls to services/projections.
- Service shims (`stateful_multi_agent/data/services.py`) pull the composition container and delegate to Application Services.

## Key Files
- `composition_root.py`: builds and wires repos, EventBus, services, projections, AI handlers, and subscribes projections
- `agent_bootstrap.py`: helper to build the agent+container and seed demo data
- `application_services/`: Order, User, Access, Course, Policy services (with tests)
- `read_models/`: Projections (User Access, Course Catalog, Order History, Policy Usage, Revenue Summary)
- `stateful_multi_agent/tools.py`: tool adapters used by sub-agents
- `stateful_multi_agent/customer_service_agent/`: main chat agent and sub-agents

## Verifying Projections
After seeding, projections are populated via events. For example:
- CourseCatalogProjection: contains “Course A” and “Course B”
- OrderHistoryProjection: has one order for the seeded user
- UserAccessProjection: updates when `grant_access` tool is used

## Optional Next Steps
- Replace echo in `agent_bootstrap.py` with your ADK chat loop
- Add user events from `UserApplicationService` (e.g., UserRegistered) for richer agent reactions
- Add more tools for projections (e.g., show revenue, show policy usage)
- Improve formatting of tool responses for better UX
