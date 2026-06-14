from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types
import asyncio
import requests

#Mock DB data
USERS_DB = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Alice", "email": "alice2@example.com"},
]


#GRAPHQL Search tool
def search_users_by_name(name : str) -> str:
    """
    Search users by name from internal user database.
    Use when the user asks about users or people.
    """

    results = [u for u in USERS_DB if u["name"].lower() == name.lower()]

    if not results:
        return "No users found."
    
    return "\n".join(
        f"ID: {u['id']}, Name: {u['name']}, Email: {u['email']}" for u in results
    )

#Countries GRAPHQL API
def search_country_by_name(name :str) -> str:
    """
    Search countries using a GraphQL API.
    Use when the user asks about countries, capitals, or country info.
    """
    query = """ 
    query ($name :String!){
    
        countries(filter: {name: {regex : $name}}) {
            code
            name
            capital
        }
    }
    """

    variables = {"name": name}

    response = requests.post(
        "https://countries.trevorblades.com/graphql",
        json = {"query" : query, "variables": variables}
    )

    data= response.json()

    countries = data["data"]["countries"]

    if not countries:
        return "No countries found."
    
    return "\n".join(
        f"Code: {c['code']}, Name: {c['name']}, Capital: {c['capital']}" for c in countries
    )

#tool
def add_numbers(a: int, b: int) -> str:
    return f"The sum of {a} and {b} is {a + b}."



async def main():
    model = LiteLlm(model="ollama_chat/qwen2.5:1.5b")

    agent = Agent(
        name = "simple_search_agent",
        model = model,
        description = "A beginner GraphQL search agent",
        instruction = "You are a search assistant. "
            "Use the GraphQL search tool to answer user queries. "
            "Return results exactly as provided.",

        tools = [search_country_by_name, search_users_by_name, add_numbers]
    )

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name = "ollama_search_app",
        user_id= "user1",
        session_id= "session1"
    )

    runner = Runner(
        agent=agent,
        app_name= "ollama_search_app",
        session_service=session_service)

    print("Google simple ADK search agent (type 'exit' to quit)")

    while True:
        user_input = input("\n>  ")
        if user_input.strip().lower() == "exit":
            break   

        content = types.Content(
            role = "user",
            parts = [types.Part (text = user_input)]
        )

        async for event in runner.run_async(
            user_id="user1",
            session_id="session1",
            new_message=content
        ):
            if event.is_final_response():
                print("\nAgent: " + event.content.parts[0].text)

   

if __name__ == "__main__":
   asyncio.run(main())