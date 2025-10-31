# IT Developers Platform Multi-Agent System

## Overview

This is an example of a multi-agent system implementing a customer service platform for an online learning platform. The system demonstrates the use of specialized agents with different roles, sharing a common state and coordinating to provide comprehensive customer service.

> New: An event-driven Application layer with projections and a bootstrap script make it easy to run a local demo and let the main agent use internal tools to perform operations.

## Quickstart

See `QUICKSTART.md` for step-by-step instructions.

- Local demo: `python3 stateful-multi-agent/agent_bootstrap.py`
- Seeds a policy, two courses, a user, and an order (via Application Services)
- Projections update via domain events; AI handlers react to events
- Integrate with your ADK chat runtime using `get_agent_container_and_seed()` from `agent_bootstrap.py`

## Architecture

### Main Agent
- **Customer Service Agent**: Central coordinator that uses tools to fulfill user requests (list courses, place orders, request refunds, etc.).

### Sub-Agents
1. **Course Support Agent**: Course content queries and learning assistance
2. **Sales Agent**: Course sales and basic order creation
3. **Policy Agent**: Policy lookup and management
4. **Order Agent**: Purchase history and refunds

### Application Services (Event-driven)
- Order, User, Access, Course, Policy services orchestrate aggregates via repositories and emit domain events (synchronously in the demo).
- Events drive projections (read models) and AI handlers.

### Projections (Read Models)
- `UserAccessProjection`, `CourseCatalogProjection`, `OrderHistoryProjection`, `PolicyUsageProjection`, `RevenueSummaryProjection`
- Subscribed to relevant events; provide fast queries for the agent tools.

### Event Flow (Demo)
```
User request → Agent decides tool → Tool calls Application Service →
Service saves state + publishes event → EventBus → Projections & AI Handlers update →
Agent replies using fresh projection data
```

## State Management

The system maintains shared state across agents and projections, including:
- User and order information
- Course catalog
- Access records and progress
- Policy metadata

## Tools and Capabilities

Each sub-agent uses tools that internally call Application Services or read models:
- Course information retrieval
- Order creation and refunds
- Policy info and creation
- Access management

## Usage Example (ADK)

```python
from agent_bootstrap import get_agent_container_and_seed
agent, container, ids = get_agent_container_and_seed()
# Hand `agent` to your ADK Runner; tools will call services internally
```

## Important Notes

- EventBus supports lightweight events using `__event_type__` for local demo
- Projections are subscribed via a `ProjectionEventHandler`
- Synchronous `publish_sync` makes updates immediate for CLI/agent demos

## Future Improvements

- Add user-related events to UserApplicationService (e.g., UserRegistered)
- Format tool responses for improved UX
- Add more tools (show revenue, policy usage summaries)