"""Single agent with three tools, driven from a terminal chat loop."""

import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from search_agent.agent import root_agent

APP_NAME = "ollama_search_app"
USER_ID = "user1"
SESSION_ID = "session1"


async def main():
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )

    runner = Runner(
        agent=root_agent, app_name=APP_NAME, session_service=session_service
    )

    print("Google ADK search agent (type 'exit' to quit)")

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        content = types.Content(role="user", parts=[types.Part(text=user_input)])

        async for event in runner.run_async(
            user_id=USER_ID, session_id=SESSION_ID, new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print("\nAgent:", event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
