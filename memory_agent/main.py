import asyncio
from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from memory_agent import memory_agent
from utils import call_agent_async

# Load environment variables from a .env file
load_dotenv()

# Initialize database session service with SQLite database URL
db_url = "sqlite:///./my_agent_data.db"
session_service = DatabaseSessionService(db_url=db_url)

# Define the initial state for a new session
initial_state = {
    "user_name": "John Doe",
    "reminders": []
}


async def main_async():
    # Define application and user identifiers
    APP_NAME = "Memory Agent"
    USER_ID = "user123"

    # Check for existing sessions for the user
    existing_sessions_response = await session_service.list_sessions(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    # Access the sessions from the response
    existing_sessions = existing_sessions_response.sessions

    # Determine whether to continue an existing session or create a new one
    if existing_sessions and len(existing_sessions) > 0:
        SESSION_ID = existing_sessions[0].id
        print(f"Continuing existing session: {SESSION_ID}")
    else:
        new_session = await session_service.create_session(
            app_name=APP_NAME,
            user_id=USER_ID,
            state=initial_state,
        )
        SESSION_ID = new_session.id
        print(f"Created new session: {SESSION_ID}")

    # Initialize the agent runner with the session service
    runner = Runner(
        agent=memory_agent,
        app_name=APP_NAME,
        session_service=session_service)

    # Start the interactive loop for user input
    print("Welcome to the Memory Agent!")
    print("Type 'exit' to end the conversation.\n")

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Exiting...")
            break

        # Process the user input asynchronously
        await call_agent_async(runner, USER_ID, SESSION_ID, user_input)


if __name__ == "__main__":
    # Run the main asynchronous function
    asyncio.run(main_async())