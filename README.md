# ADK + Ollama Agents

Small experiments with [Google's Agent Development Kit (ADK)](https://google.github.io/adk-docs/) running fully **locally** on an [Ollama](https://ollama.com/) model through [LiteLLM](https://docs.litellm.ai/). No API keys and no cloud.

I wrote this while learning ADK, so it stays small and readable on purpose.

## What's inside

| File | What it shows |
| --- | --- |
| [`search_agent/`](search_agent/) | An ADK agent package with `root_agent`. Works with `adk web` and `adk run`. |
| [`search_agent/tools.py`](search_agent/tools.py) | Plain Python functions used as tools: a mock user DB, a live GraphQL countries API, and an adder. |
| [`single_agent.py`](single_agent.py) | One agent with three tools, driven by a terminal chat loop with `Runner` and `InMemorySessionService`. |
| [`multi_agent.py`](multi_agent.py) | Manual multi-agent routing. An orchestrator classifies each question as `USER` or `COUNTRY`, then hands it to the matching specialist agent. |

```
            ┌──────────────────────┐
  question ─► orchestrator_agent   │── "USER" ───► user_agent    ─► search_users_by_name
            │ (classifies only)    │── "COUNTRY" ► country_agent ─► search_country_by_name (GraphQL)
            └──────────────────────┘
```

## Setup

1. **Install Ollama and pull a model that supports tool calling:**

   ```bash
   ollama pull qwen2.5:1.5b
   ```

2. **Create a virtual environment and install the dependencies:**

   ```bash
   python -m venv .venv
   # Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. *(Optional)* To use a different model or Ollama host, copy `search_agent/.env.example` to `search_agent/.env` and edit it, or set `OLLAMA_MODEL` in your shell.

## Run

```bash
# Terminal chat with the single agent
python single_agent.py

# Terminal chat with the orchestrator + specialists
python multi_agent.py

# ADK's browser dev UI (choose "search_agent"), with event traces
adk web
```

Questions to try:

- `Find users named Alice`
- `What is the capital of Japan?`
- `What is 12 plus 30?`

## Notes and lessons learned

- **Model prefix:** use `ollama_chat/<model>`, not `ollama/<model>`. The chat endpoint handles tool calls much more reliably.
- **Small models are flaky:** a 1.5B model sometimes skips a tool or ignores the one-word routing rule. Larger models such as `qwen2.5:7b` or `llama3.1:8b` behave better.
- **Tools are just functions:** ADK reads the name, type hints and docstring, so a clear docstring is effectively the tool's prompt.
- **Routing is done by hand here** to show the mechanics. ADK can also do this natively with `sub_agents=[...]` and LLM-driven delegation, which is a natural next step.

## License

[MIT](LICENSE)
