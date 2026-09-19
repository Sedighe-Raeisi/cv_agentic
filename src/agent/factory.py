import os

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI


def get_llm(provider: str = None) -> BaseChatModel:
    """
    Factory function to switch between Academic Cloud API, standard OpenAI, or local Ollama.
    All secrets are pulled dynamically from environment variables.
    """
    provider = provider or os.getenv("PROVIDER", "academiccloud")

    if provider == "academiccloud":
        api_key = os.getenv("ACADEMIC_API_KEY")
        base_url = os.getenv("ACADEMIC_BASE_URL", "https://chat-ai.academiccloud.de/v1")
        model_name = os.getenv("ACADEMIC_MODEL", "meta-llama-3.1-8b-instruct")

        if not api_key:
            raise ValueError(
                "Missing ACADEMIC_API_KEY environment variable. "
                "Please add ACADEMIC_API_KEY=your_key to your local .env file."
            )

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.2,
        )

    elif provider == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("Missing OPENAI_API_KEY in environment variables.")

        return ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            api_key=api_key,
            temperature=0.2,
        )

    elif provider == "ollama":
        return ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "qwen2.5-coder"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0.2,
        )

    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")