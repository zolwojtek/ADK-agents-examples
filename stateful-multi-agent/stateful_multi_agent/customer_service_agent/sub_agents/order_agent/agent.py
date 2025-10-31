"""
Order agent implementation.
"""

from pathlib import Path
from google.adk.agents import Agent

from ....tools import (
    GetUserOrdersTool,
    RequestRefundTool,
    ProcessRefundTool
)
from ....data.services import OrderService
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

# Initialize service
order_service = OrderService(order_repo, course_repo, policy_repo)

# Initialize tools
get_orders_tool = GetUserOrdersTool(order_service)
request_refund_tool = RequestRefundTool(order_service)
process_refund_tool = ProcessRefundTool(order_service)

# Load prompt
PROMPT_DIR = Path(__file__).parent / "prompts"
prompt = YAMLPrompt(PROMPT_DIR / "order.yaml")

# Validate prompt
if not prompt.validate():
    raise ValueError("Invalid prompt template")

order_agent = Agent(
    name="order_agent",
    model="gemini-2.5-flash",
    description="Order management agent",
    instruction=prompt.template,
    tools=[
        get_orders_tool,
        request_refund_tool,
        process_refund_tool
    ],
)