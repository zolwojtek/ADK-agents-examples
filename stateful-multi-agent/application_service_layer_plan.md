# Application Service Layer: Architectural Plan

## Purpose and Role

Application services are the core orchestration layer for all business use cases (aka "interactors" or "use case controllers").
- Coordinators of domain logic—not data holders, not UI, not infrastructure.
- Mediate commands, workflow, and transactions that span multiple aggregates, repositories, and external interfaces.
- Provide a stable API boundary for external systems (APIs, UI, jobs, etc) to engage the domain model.

---

## Key Responsibilities
- Accept commands or input DTOs for a use case (e.g., PlaceOrder, RegisterUser, GrantAccess).
- Validate input/coarse-level business rule enforcement before deeper domain logic.
- Load/manipulate one or more aggregates via repositories.
- Delegate complex logic to domain services when necessary.
- Raise/publish domain events.
- Commit state and coordinate atomic/transactional integrity where possible.
- Return output DTOs or result objects for the outcome (and/or raise exceptions).

### What They Should NOT Do
- **No direct persistence/ORM/data access** except through repositories.
- **No UI/view logic** or presentation formatting.
- **No business logic that belongs in aggregates (invariants!) or domain services.**
- **No direct infrastructure (e.g., email, payment gateways):** delegate to domain events + handlers or adapters.

---

## Relationships

- **Aggregates:** Application services load/save/manage aggregate roots via repository abstractions.
- **Repositories:** The bridge for persistence access—services never know about the underlying storage.
- **Domain Services:** Use for pure domain logic that cannot live in aggregates (e.g., orchestration involving many aggregates).
- **Projections/Read Models:** Application services write to the domain, projections/read models are updated independently based on events.

---

## Directory Layout

Recommended structure:
```
application_services/
  order_service.py
  user_service.py
  access_service.py
  ...
  __init__.py
```
- Service per major use case cluster/domain.
- Each exposes a class: `OrderApplicationService`, `UserApplicationService`, etc.
- Group cross-cutting logic/utilities in `application_services/utils.py` if needed.

---

## Naming Guidelines
- Classes: `FooApplicationService` (never just "Service")
- Methods: `place_order`, `request_refund`, `grant_access`, `register_user`, etc.—corresponding to use cases/commands.
- DTOs as needed: `PlaceOrderCommand`, `OrderResult`, etc.

---

## Patterns/Workflow

- **Command/DTO acceptance:**
  ```python
  class PlaceOrderCommand(BaseModel):
      user_id: str
      course_ids: List[str]
      ...
  ```
- **Typical orchestration method:**
  ```python
  def place_order(self, cmd: PlaceOrderCommand) -> OrderResult:
      user = self.user_repo.get_by_id(cmd.user_id)
      ...
      order = Order.aggregate(...) # domain logic
      self.order_repo.save(order)
      # Optionally publish events
      return OrderResult(...)
  ```
- **Transaction management:** Use Unit of Work patterns if multi-aggregate
- **Exception management:** Distinguish between input validation, business rule violations (domain errors), and infrastructure failures.

---

## Example: OrderApplicationService Interface (Python/pseudocode)
```python
class OrderApplicationService:
    def __init__(self, order_repo, user_repo, event_bus):
        ...

    def place_order(self, cmd: PlaceOrderCommand) -> OrderResult:
        ...

    def request_refund(self, cmd: RequestRefundCommand) -> RefundResult:
        ...

    ... # more use cases
```

---

## Testing Strategy
- Test application services as black-box orchestrators: mock repositories, domain services, event bus.
- Focus on integration with surrounding layers, command/result validity, error handling, and event emission.
- Use scenario-based tests mimicking input + asserting side effects and outputs.

---

## Roadmap for Implementation
**1. Prioritize high-value use cases:** (Orders, Refunds, User Reg, Access, etc)
**2. Implement one service at a time, starting with OrderApplicationService**
**3. Stub all dependencies (repositories, event_bus) for testing**
**4. Expand functionality and integration as needed for core business workflows**

---

This plan ensures decoupling, testability, and scalable orchestration of your core DDD components.
