from google.adk.agents import Agent

question_agent = Agent(
    name="question_agent",
    model="gemini-2.5-flash",
    description="Question agent",
    instruction="""
        You are a helpful assistant that can answer user's questions

        Here is some information about the user:
        Name: 
        {user_name}
        Preferences: 
        {user_preferences}
        """,
)
