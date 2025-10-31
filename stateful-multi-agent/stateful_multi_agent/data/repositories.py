from typing import Any

# Shim repository classes for compatibility with sub_agent imports.
# Actual access is performed via composition_root container inside services.

class OrderRepository:
    def __init__(self) -> None:
        pass

class CourseRepository:
    def __init__(self) -> None:
        pass

class PolicyRepository:
    def __init__(self) -> None:
        pass
