"""Agent definition picked up by `adk web` / `adk run` (they look for `root_agent`)."""

from google.adk.agents import Agent

from .config import get_model
from .tools import add_numbers, search_country_by_name, search_users_by_name

root_agent = Agent(
    name="search_agent",
    model=get_model(),
    description="A beginner search agent backed by a local Ollama model.",
    instruction=(
        "You are a search assistant. "
        "Use the tools to answer questions about users, countries and sums. "
        "Return tool results exactly as provided."
    ),
    tools=[search_country_by_name, search_users_by_name, add_numbers],
)
