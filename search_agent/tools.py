"""Tools shared by every agent in this repo.

ADK turns plain Python functions into tools: the function name, type hints
and docstring are what the model sees when deciding which tool to call.
"""

import requests

COUNTRIES_API = "https://countries.trevorblades.com/graphql"

# Mock "database" so the user tool works without any setup.
USERS_DB = [
    {"id": 1, "name": "Alice", "email": "alice@example.com"},
    {"id": 2, "name": "Bob", "email": "bob@example.com"},
    {"id": 3, "name": "Alice", "email": "alice2@example.com"},
]


def search_users_by_name(name: str) -> str:
    """
    Search users by name from the internal user database.
    Use when the user asks about users, people or emails.
    """
    results = [u for u in USERS_DB if u["name"].lower() == name.lower()]

    if not results:
        return "No users found."

    return "\n".join(
        f"ID: {u['id']}, Name: {u['name']}, Email: {u['email']}" for u in results
    )


def search_country_by_name(name: str) -> str:
    """
    Search countries using a public GraphQL API.
    Use when the user asks about countries, capitals, or country info.
    """
    query = """
    query ($name: String!) {
        countries(filter: {name: {regex: $name}}) {
            code
            name
            capital
        }
    }
    """

    try:
        response = requests.post(
            COUNTRIES_API,
            json={"query": query, "variables": {"name": name}},
            timeout=10,
        )
        response.raise_for_status()
        countries = response.json()["data"]["countries"]
    except (requests.RequestException, KeyError, TypeError) as e:
        return f"Country lookup failed: {e}"

    if not countries:
        return "No countries found."

    return "\n".join(
        f"Code: {c['code']}, Name: {c['name']}, Capital: {c['capital']}"
        for c in countries
    )


def add_numbers(a: int, b: int) -> str:
    """Add two integers. Use when the user asks for a sum."""
    return f"The sum of {a} and {b} is {a + b}."
