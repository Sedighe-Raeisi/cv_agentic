import os

from dotenv import load_dotenv
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI

load_dotenv(override=True)
provider = os.getenv("PROVIDER")
print("===================================")
print(f"Using LLM provider: {provider}")
print("===================================")

def get_llm(provider: str = None) -> BaseChatModel:
    """
    Factory function to switch between Academic Cloud API, standard OpenAI, or local Ollama.
    All secrets are pulled dynamically from environment variables.
    """
    

    if provider is None or provider == "academiccloud":
        
        provider = "academiccloud"
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL", "https://chat-ai.academiccloud.de/v1")
        model_name = os.getenv("LLM_MODEL", "meta-llama-3.1-8b-instruct")
        print("===================================")
        print(f" Provider: {provider}, base_url = {base_url}, model_name = {model_name}")
        print("===================================")
        if not api_key:
            raise ValueError(
                "Missing LLM_API_KEY environment variable. "
                "Please add LLM_API_KEY=your_key to your local .env file."
            )

        return ChatOpenAI(
            model=model_name,
            api_key=api_key,
            base_url=base_url,
            temperature=0.2,
            timeout=180,
            max_retries=2
        )
    elif provider == "gemini":
            api_key = os.getenv("GEMINI_API_KEY")
            if not api_key:
                raise ValueError("GEMINI_API_KEY is missing in your .env file.")
            
            # gemini-1.5-flash natively supports multimodal base64 image inputs
            return ChatGoogleGenerativeAI(
                model="gemini-1.5-flash",
                google_api_key=api_key,
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