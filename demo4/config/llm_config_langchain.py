import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_google_vertexai import ChatVertexAI
# --- NEW: Import the rate limiter ---
from langchain_core.rate_limiters import InMemoryRateLimiter

# Load .env as fallback
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")

# --- NEW: Create a global rate limiter (15 RPM = 0.25 requests per second) ---
# This ensures all calls to get_llm() share the same request bucket
rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.25, 
    check_every_n_seconds=0.1, 
    max_bucket_size=1
)

def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ValueError(f"Missing required environment variable: {name}")
    return value

def get_llm():
    """
    Return the LangChain LLM with built-in rate limits and automatic retries.
    """
    backend = _get_env("LLM_BACKEND", "vertex_ai").strip().lower()
    model_name = _get_env("MODEL_NAME", required=True)
    temperature = float(_get_env("LLM_TEMPERATURE", "0"))

    if backend == "vertex_ai":
        project = _get_env("VERTEXAI_PROJECT", required=True)
        location = _get_env("VERTEXAI_LOCATION", "us-central1")

        # 1. Initialize the LLM and attach the rate limiter
        base_llm = ChatVertexAI(
            model=model_name,
            project=project,
            location=location,
            temperature=temperature,
            rate_limiter=rate_limiter, # Applies the 15 RPM limit
        )

        # 2. Wrap the LLM in an automatic retry mechanism for 429 errors
        llm_with_retries = base_llm.with_retry(
            stop_after_attempt=15,
            wait_exponential_jitter=True
        )

        return llm_with_retries

    raise ValueError(f"Unsupported LLM_BACKEND: {backend}")