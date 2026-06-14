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

# #tool
# def add_numbers(a: int, b: int) -> str:
#     return f"The sum of {a} and {b} is {a + b}."



async def main():
    model = LiteLlm(model="ollama_chat/qwen2.5:1.5b")

    #User Agent
    user_agent  =Agent (
        name = "user_agent",
        model = model,
        description= "Handles user queries",
        instruction= "Handle questions about users or emails only.", 
        tools = [search_users_by_name]
    )

    #Country Agent
    country_Agent = Agent(
        name = "country_agent",
        model = model,
        description = "Handles country queries",
        instruction= "Handles questions about countries or capitals only.",
        tools = [search_country_by_name]
    )
    
    #Orchestrator Agent
    orchestrator_agent = Agent(
        name = "orchestrator_agent",
        model = model,
        description= "Routes queries to correct agent",
        instruction= "Decide who should answer .\n"
            "If it is about users, names or emails -> USER\n"
            "If it is about countries or capitals -> COUNTRY\n"
            # "Route the user's question to the correct agent ONLY if:- The question clearly matches that agent's responsibility."
            "Respond with ONLY one word: USER or COUNTRY",

    )

    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name = "orchestrator_app",
        user_id= "user1",
        session_id= "session1"
    )

    orchestrator_runner = Runner(
        agent=orchestrator_agent,
        app_name= "orchestrator_app",
        session_service=session_service)
    

    user_runner  = Runner(
        agent  =user_agent,
        app_name= "orchestrator_app",
        session_service=session_service,
    )

    country_runner = Runner(
        agent = country_Agent,
        app_name= "orchestrator_app",
        session_service=session_service,
    )


    print("Multi Agent Orchestrator (type 'exit' to quit)")


    #main loop
    while True:
        user_input = input("\n>  ")
        if user_input.strip().lower() == "exit":
            break   

        content = types.Content(
            role = "user",
            parts = [types.Part (text = user_input)]
        )

        #1
        decision = None
        async for event in orchestrator_runner.run_async(
            user_id="user1",
            session_id="session1",
            new_message=content
        ):
            if event.is_final_response():
                decision = event.content.parts[0].text.strip().upper()

        #2
        if decision == "USER":
            runner = user_runner
        elif decision == "COUNTRY":
            runner = country_runner
        else:
            print("Agent: I am not capable of handling this request.")
            continue

        #3
        async for event in runner.run_async(
            user_id="user1",
            session_id="session1",
            new_message=content
        ):
            if event.is_final_response():
                # print("\nAgent: " + event.content.parts[0].text
                if (
                    event.content
                    and event.content.parts
                    and len(event.content.parts) > 0
                    and hasattr(event.content.parts[0], "text")
                ):
                    print("\nAgent:", event.content.parts[0].text)
   

if __name__ == "__main__":
   asyncio.run(main())