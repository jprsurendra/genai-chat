"""Provider-agnostic smoke test: Ollama or OpenAI, any model."""
import sys
from app.config import settings
from openai import OpenAI


def make_client_and_model(use_fast: bool = False) -> tuple[OpenAI, str]:
    if settings.LLM_PROVIDER == "ollama":
        model = settings.OLLAMA_MODEL_FAST if use_fast else settings.OLLAMA_MODEL
        return (
            OpenAI(base_url=settings.OLLAMA_BASE_URL, api_key="ollama"),
            model,
        )
    return (
        OpenAI(api_key=settings.OPENAI_API_KEY),
        settings.OPENAI_MODEL,
    )


def test(use_fast: bool = False) -> bool:
    client, model = make_client_and_model(use_fast)
    tag = "FAST" if use_fast else "MAIN"

    print(f"\n──── [{tag}] {settings.LLM_PROVIDER} / {model} ────")
    if settings.LLM_PROVIDER == "ollama":
        print(f"Base URL: {settings.OLLAMA_BASE_URL}")

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": settings.SYSTEM_PROMPT},
                {"role": "user", "content": "Reply with exactly: hello from the model"},
            ],
            max_tokens=20,
        )
        print("✅ SUCCESS")
        print("Response:   ", resp.choices[0].message.content)
        if resp.usage:
            print(f"Tokens used: {resp.usage.total_tokens}")
        return True
    except Exception as e:
        print("❌ FAILED")
        print(f"{type(e).__name__}: {e}")
        return False


if __name__ == "__main__":
    ok_main = test(use_fast=False)
    ok_fast = test(use_fast=True)

    print("\n" + "=" * 50)
    print(f"MAIN model: {'✅ OK' if ok_main else '❌ FAIL'}")
    print(f"FAST model: {'✅ OK' if ok_fast else '❌ FAIL'}")
    sys.exit(0 if (ok_main and ok_fast) else 1)
