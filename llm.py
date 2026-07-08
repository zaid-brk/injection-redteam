"""Pick the LLM provider once; every other file imports agent_llm / judge_llm.

Default is Google Gemini (free tier). Flip LLM_PROVIDER=openai in .env to run the
tutorial's original OpenAI setup unchanged — the code shape is identical, only the
model class and names differ. The judge is always a STRONGER model than the agent
(a weaker judge grading a stronger agent is unreliable).

ponytail: one env-var branch, not a provider-plugin framework. Two providers, one if.
"""
import os
from dotenv import load_dotenv

load_dotenv()

PROVIDER = os.getenv("LLM_PROVIDER", "gemini")  # "gemini" (free) | "openai"

# Model names are the only provider-specific detail. Bump these if a newer model ships.
# Gemini free tier only grants quota on some models (not -pro, not 2.0-flash), so the
# agent uses flash-lite and the judge uses the stronger plain flash. Both are free.
_MODELS = {
    "gemini": {"agent": "gemini-2.5-flash-lite", "judge": "gemini-2.5-flash"},
    "openai": {"agent": "gpt-4o-mini", "judge": "gpt-4o"},
}


def _model(role: str):
    """role: 'agent' (fast, cheap, the victim) or 'judge' (stronger, grades success)."""
    name = _MODELS[PROVIDER][role]
    if PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        # max_retries backs off on free-tier 429s so a long benchmark run survives them.
        return ChatGoogleGenerativeAI(model=name, temperature=0, max_retries=6)
    if PROVIDER == "openai":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model=name, temperature=0)
    raise ValueError(f"Unknown LLM_PROVIDER={PROVIDER!r}. Use 'gemini' or 'openai'.")


def agent_llm():
    return _model("agent")


def judge_llm():
    return _model("judge")
