"""Manual multi-agent routing.

An orchestrator agent classifies each question as USER or COUNTRY, then the
question is handed to the matching specialist agent.
"""

import asyncio

from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from search_agent.config import get_model
from search_agent.tools import search_country_by_name, search_users_by_name

APP_NAME = "orchestrator_app"
USER_ID = "user1"


async def ask(runner: Runner, session_id: str, content: types.Content) -> str | None:
    """Run one turn and return the agent's final text, if any."""
    final_text = None
    async for event in runner.run_async(
        user_id=USER_ID, session_id=session_id, new_message=content
    ):
        if event.is_final_response() and event.content and event.content.parts:
            final_text = event.content.parts[0].text
    return final_text


async def main():
    model = get_model()

    user_agent = Agent(
        name="user_agent",
        model=model,
        description="Handles user queries",
        instruction="Handle questions about users or emails only.",
        tools=[search_users_by_name],
    )

    country_agent = Agent(
        name="country_agent",
        model=model,
        description="Handles country queries",
        instruction="Handle questions about countries or capitals only.",
        tools=[search_country_by_name],
    )

    orchestrator_agent = Agent(
        name="orchestrator_agent",
        model=model,
        description="Routes queries to the correct agent",
        instruction=(
            "Decide who should answer.\n"
            "If it is about users, names or emails -> USER\n"
            "If it is about countries or capitals -> COUNTRY\n"
            "Respond with ONLY one word: USER or COUNTRY"
        ),
    )

    # Each agent gets its own session so the orchestrator's one-word answers
    # don't end up in the specialists' conversation history.
    session_service = InMemorySessionService()
    runners = {}
    for key, agent in [
        ("ORCHESTRATOR", orchestrator_agent),
        ("USER", user_agent),
        ("COUNTRY", country_agent),
    ]:
        await session_service.create_session(
            app_name=APP_NAME, user_id=USER_ID, session_id=key
        )
        runners[key] = Runner(
            agent=agent, app_name=APP_NAME, session_service=session_service
        )

    print("Multi-agent orchestrator (type 'exit' to quit)")

    while True:
        user_input = input("\n> ").strip()
        if user_input.lower() == "exit":
            break
        if not user_input:
            continue

        content = types.Content(role="user", parts=[types.Part(text=user_input)])

        # 1. Ask the orchestrator where the question should go.
        decision = await ask(runners["ORCHESTRATOR"], "ORCHESTRATOR", content)
        decision = (decision or "").strip().upper()

        # 2. Hand it to the matching specialist.
        if decision not in ("USER", "COUNTRY"):
            print("\nAgent: I am not capable of handling this request.")
            continue

        print(f"[routed to {decision.lower()}_agent]")
        answer = await ask(runners[decision], decision, content)
        if answer:
            print("\nAgent:", answer)


if __name__ == "__main__":
    asyncio.run(main())
