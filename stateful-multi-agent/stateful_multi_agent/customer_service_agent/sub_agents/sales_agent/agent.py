"""
Sales agent implementation.
"""

from pathlib import Path
from google.adk.agents import Agent

from ....tools import (
    CreateOrderTool,
    CompleteOrderTool,
    GetCoursesTool
)
from ....data.services import (
    OrderService,
    CourseService
)
from ....data.repositories import (
    OrderRepository,
    CourseRepository,
    PolicyRepository
)
from ...prompts.base_prompt import YAMLPrompt

# Initialize repositories
order_repo = OrderRepository()
course_repo = CourseRepository()
policy_repo = PolicyRepository()

# Initialize services
order_service = OrderService(order_repo, course_repo, policy_repo)
course_service = CourseService(course_repo)

# Initialize tools
create_order_tool = CreateOrderTool(order_service)
complete_order_tool = CompleteOrderTool(order_service)
get_courses_tool = GetCoursesTool(course_service)

# Load prompt
PROMPT_DIR = Path(__file__).parent / "prompts"
prompt = YAMLPrompt(PROMPT_DIR / "sales.yaml")

# Validate prompt
if not prompt.validate():
    raise ValueError("Invalid prompt template")

sales_agent = Agent(
    name="sales_agent",
    model="gemini-2.5-flash",
    description="Sales agent",
    instruction=prompt.template,
    tools=[
        create_order_tool,
        complete_order_tool,
        get_courses_tool
    ],
)