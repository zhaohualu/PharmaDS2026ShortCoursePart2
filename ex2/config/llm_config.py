import os
from pathlib import Path

from dotenv import load_dotenv
from crewai import LLM

# Always load the .env from the project root (folder containing main_crewai.py)
PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_llm() -> LLM:
    """
    Provider-agnostic LLM configuration layer for CrewAI.

    Supported backends:
    - openai_compatible: local vLLM or any OpenAI-style endpoint
    - vertex_ai: Gemini models on Google Cloud Vertex AI
    - gemini: Gemini API key path (not recommended for Vertex Workbench use)
    """
    backend = _get_env("LLM_BACKEND", "vertex_ai").strip().lower()
    raw_model_name = _get_env("MODEL_NAME", required=True)
    temperature = float(_get_env("LLM_TEMPERATURE", "0"))

    if backend == "openai_compatible":
        base_url = _get_env("OPENAI_API_BASE", required=True)
        api_key = _get_env("OPENAI_API_KEY", "EMPTY")

        model_name = raw_model_name
        if not raw_model_name.startswith("openai/"):
            model_name = f"openai/{raw_model_name}"

        return LLM(
            model=model_name,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
        )

    if backend == "vertex_ai":
        vertex_project = _get_env("VERTEXAI_PROJECT", required=True)
        vertex_location = _get_env("VERTEXAI_LOCATION", "global")

        model_name = raw_model_name
        if not raw_model_name.startswith("vertex_ai/"):
            model_name = f"vertex_ai/{raw_model_name}"

        # LiteLLM supports Vertex AI Gemini with vertex_project / vertex_location,
        # and ADC on Workbench handles authentication.
        return LLM(
            model=model_name,
            temperature=temperature,
            vertex_project=vertex_project,
            vertex_location=vertex_location,
        )

    if backend == "gemini":
        # This branch is for Gemini API / AI Studio style usage, not Vertex AI Workbench.
        api_key = _get_env("GEMINI_API_KEY", required=True)

        model_name = raw_model_name
        if not raw_model_name.startswith("gemini/"):
            model_name = f"gemini/{raw_model_name}"

        return LLM(
            model=model_name,
            api_key=api_key,
            temperature=temperature,
        )

    raise ValueError(
        "Unsupported LLM_BACKEND. Expected one of: "
        "openai_compatible, vertex_ai, gemini"
    )

    