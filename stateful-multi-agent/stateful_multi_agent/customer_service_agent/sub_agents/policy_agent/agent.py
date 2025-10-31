"""
Policy agent implementation.
"""

from pathlib import Path
from google.adk.agents import Agent

from ....tools import (
    GetPolicyTool,
    GetRefundPolicyTool,
    CreatePolicyTool,
    AddPolicyVersionTool,
    ActivatePolicyTool
)
from ....data.services import PolicyService
from ....data.repositories import PolicyRepository
from ...prompts.base_prompt import YAMLPrompt

# Initialize repository and service
policy_repo = PolicyRepository()
policy_service = PolicyService(policy_repo)

# Initialize tools
get_policy_tool = GetPolicyTool(policy_service)
get_refund_policy_tool = GetRefundPolicyTool(policy_service)
create_policy_tool = CreatePolicyTool(policy_service)
add_version_tool = AddPolicyVersionTool(policy_service)
activate_policy_tool = ActivatePolicyTool(policy_service)

# Load prompt
PROMPT_DIR = Path(__file__).parent / "prompts"
prompt = YAMLPrompt(PROMPT_DIR / "policy.yaml")

# Validate prompt
if not prompt.validate():
    raise ValueError("Invalid prompt template")

policy_agent = Agent(
    name="policy_agent",
    model="gemini-2.5-flash",
    description="Policy agent",
    instruction=prompt.template,
    tools=[
        get_policy_tool,
        get_refund_policy_tool,
        create_policy_tool,
        add_version_tool,
        activate_policy_tool
    ],
)