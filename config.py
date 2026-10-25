"""Provider-independent configuration for a future AI API connection."""

from dataclasses import dataclass, field
import math
import os
from typing import Mapping
from urllib.parse import urlsplit

from dotenv import load_dotenv


AI_MODEL = "nvidia/nemotron-3.5-super-vl:free"


@dataclass(frozen=True)
class AIConfig:
    """AI connection settings; the API key is deliberately omitted from repr."""

    api_key: str = field(repr=False)
    base_url: str
    model: str
    timeout_seconds: float = 30.0


def load_ai_config(env: Mapping[str, str] | None = None) -> AIConfig:
    """Load AI settings from environment variables and, by default, local .env.

    AI_API_KEY and AI_API_BASE_URL are required. The model defaults to the
    configured AI_MODEL constant and can be overridden with the AI_MODEL
    environment variable. The endpoint and model are caller-configurable, so
    this module assumes no particular API provider.
    Supplying ``env`` makes loading deterministic and skips reading a .env file.
    """
    if env is None:
        load_dotenv(override=False)
        values: Mapping[str, str] = os.environ
    else:
        values = env

    api_key = values.get("AI_API_KEY", "").strip()
    base_url = values.get("AI_API_BASE_URL", "").strip()
    model = values.get("AI_MODEL", "").strip() or AI_MODEL
    timeout_text = values.get("AI_TIMEOUT_SECONDS", "30").strip()

    missing = [name for name, value in (
        ("AI_API_KEY", api_key),
        ("AI_API_BASE_URL", base_url),
    ) if not value]
    if missing:
        raise ValueError("Missing required AI configuration: " + ", ".join(missing))

    parsed_url = urlsplit(base_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise ValueError("AI_API_BASE_URL must be an absolute HTTP or HTTPS URL.")

    try:
        timeout_seconds = float(timeout_text)
    except ValueError as exc:
        raise ValueError("AI_TIMEOUT_SECONDS must be a positive number.") from exc
    if not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("AI_TIMEOUT_SECONDS must be a positive number.")

    return AIConfig(
        api_key=api_key,
        base_url=base_url,
        model=model,
        timeout_seconds=timeout_seconds,
    )
