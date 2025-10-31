"""
Customer service agent implementation.
"""

from pathlib import Path
from google.adk.agents import Agent

from .sub_agents.course_support_agent.agent import course_support_agent
from .sub_agents.sales_agent.agent import sales_agent
from .sub_agents.policy_agent.agent import policy_agent
from .sub_agents.order_agent.agent import order_agent
from .prompts.base_prompt import YAMLPrompt

# Load prompt
PROMPT_DIR = Path(__file__).parent / "prompts"
prompt = YAMLPrompt(PROMPT_DIR / "customer_service.yaml")

# Validate prompt
if not prompt.validate():
    raise ValueError("Invalid prompt template")

# Create customer service agent
CustomerServiceAgent = Agent(
    name="customer_service_agent",
    model="gemini-2.5-flash",
    description="Customer service agent for handling course-related inquiries and operations",
    instruction=prompt.template,
    sub_agents=[
        course_support_agent,
        sales_agent,
        policy_agent,
        order_agent
    ]
)

# Export the agent
__all__ = ['CustomerServiceAgent']