from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv


class ConfigurationError(RuntimeError):
    """Raised when required runtime configuration is missing."""


@dataclass(frozen=True)
class Settings:
    vworld_api_key: str | None
    land_api_key: str | None
    default_legal_dong_code: str | None = None


def load_settings() -> Settings:
    """Load settings from .env and process environment variables."""
    load_dotenv()
    return Settings(
        vworld_api_key=_clean(os.getenv("VWORLD_API_KEY")),
        land_api_key=_clean(os.getenv("LAND_API_KEY")),
        default_legal_dong_code=_clean(os.getenv("LEGAL_DONG_CODE")),
    )


def require_api_key(value: str | None, name: str) -> str:
    if not value:
        raise ConfigurationError(f"{name} is required. Set it in the environment or .env file.")
    return value


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None
