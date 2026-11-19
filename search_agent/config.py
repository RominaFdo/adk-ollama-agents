import os

from google.adk.models.lite_llm import LiteLlm

# Any Ollama model you have pulled works, as long as it supports tool calling.
# Override with e.g.  OLLAMA_MODEL=llama3.2:3b
MODEL_NAME = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")


def get_model() -> LiteLlm:
    # "ollama_chat/" makes LiteLLM use Ollama's /api/chat endpoint, which
    # handles tool calls better than the plain "ollama/" prefix.
    return LiteLlm(model=f"ollama_chat/{MODEL_NAME}")
