from google.adk.agents import Agent

root_agent = Agent(
    name="greeting_agent",
    model="gemini-2.5-flash",
    description="Greeting agent",
    instruction="You are a helpful assistant that greets the user",
)