from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

'''
class Settings:
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    SYSTEM_PROMPT: str = (
        "You are a helpful, concise AI assistant. "
        "Use markdown for formatting. Use code blocks for code."
    )

settings = Settings()
'''


class Settings:
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "ollama")

    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.2:1b")
    OLLAMA_MODEL_FAST: str = os.getenv("OLLAMA_MODEL_FAST", "qwen2.5:1.5b")

    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    SYSTEM_PROMPT: str = (
        "You are a helpful, concise AI assistant. "
        "Use markdown for formatting. Use code blocks for code."
    )


settings = Settings()

if settings.LLM_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
    raise RuntimeError("❌ LLM_PROVIDER=openai but OPENAI_API_KEY is not set in .env")

if settings.LLM_PROVIDER not in ("ollama", "openai"):
    raise RuntimeError(
        f"❌ Unknown LLM_PROVIDER='{settings.LLM_PROVIDER}'. Use 'ollama' or 'openai'."
    )
    
    
