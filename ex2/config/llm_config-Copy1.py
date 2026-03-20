import os
from dotenv import load_dotenv
from crewai import LLM

load_dotenv()


def _get_env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and (value is None or str(value).strip() == ""):
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def get_llm() -> LLM:
    """
    Provider-agnostic LLM configuration layer for CrewAI.

    Current setup:
    - local vLLM server exposing an OpenAI-compatible API

    Future setup:
    - Gemini
    """
    backend = _get_env("LLM_BACKEND", "openai_compatible").strip().lower()
    raw_model_name = _get_env(
        "MODEL_NAME",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-32B",
        required=True,
    )
    temperature = float(_get_env("LLM_TEMPERATURE", "0"))

    if backend == "openai_compatible":
        base_url = _get_env("OPENAI_API_BASE", required=True)
        api_key = _get_env("OPENAI_API_KEY", "EMPTY")

        # LiteLLM needs an explicit provider prefix for OpenAI-compatible endpoints.
        # Example: openai/<model-name>
        model_name = raw_model_name
        if not raw_model_name.startswith("openai/"):
            model_name = f"openai/{raw_model_name}"

        return LLM(
            model=model_name,
            base_url=base_url,
            api_key=api_key,
            temperature=temperature,
        )

    if backend == "gemini":
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
        "openai_compatible, gemini"
    )
