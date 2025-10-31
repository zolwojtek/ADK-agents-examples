from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.it_agent.agent import it_agent
from .sub_agents.news_agent.agent import news_agent
from .sub_agents.stock_agent.agent import stock_agent
from .tools.tools import get_current_time

root_agent = Agent(
    name="manager_agent",
    model="gemini-2.5-flash",
    description="A manager for other sub-agents",
    instruction="""
       You are a manager agent responsible for delegating tasks to other sub-agents.

       Always delegate tasks to the most appropriate sub-agent based on our best judgement over user's request.

       You are responsible for delegating tasks to the following sub-agents:
       - it_agent
       - stock_agent

       You ale have access to the following tools:
       - get_current_time
       - news_agent
    """,
    sub_agents=[it_agent, stock_agent],
    tools=[get_current_time, AgentTool(news_agent)],
)