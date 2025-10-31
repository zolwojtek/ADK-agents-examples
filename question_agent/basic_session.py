import uuid
import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from question_agent import question_agent

load_dotenv()

async def main():
    session_service = InMemorySessionService()

    initial_state = {
        "user_name": "John Doe",
        "user_preferences": """
            He is a software engineer. 
            He is interested in learning about AI and machine learning.
            He likes to play basketball and watch movies.
        """
    }

    APP_NAME = "Question Agent"
    USER_ID = "user123"
    SESSION_ID = str(uuid.uuid4())

    session = await session_service.create_session(
        session_id=SESSION_ID,
        state=initial_state,
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    print("NEW SESSION CREATED:")
    print(f"Session ID: {SESSION_ID}")

    runner = Runner(
        agent=question_agent,
        app_name=APP_NAME,
        session_service=session_service)

    new_message = types.Content(
        role="user", 
        parts=[types.Part(text="What's John occupation?")]
    )

    for event in runner.run(
        user_id=USER_ID,
        session_id=SESSION_ID,
        new_message=new_message,
    ):
        if event.is_final_response():
            if event.content and event.content.parts:
                print(f"Response: {event.content.parts[0].text}")

    print("---SESSION LOGS---")
    session_temp = await session_service.get_session(
        app_name=APP_NAME,
        session_id=SESSION_ID,
        user_id=USER_ID,
    )

    print(f"SESSION STATE:")
    for key, value in session_temp.state.items():
        print(f"{key}: {value}")

if __name__ == "__main__":
    asyncio.run(main())