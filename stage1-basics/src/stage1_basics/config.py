from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True, slots=True)
class AppConfig:
    base_url: str
    api_key: str


def load_config() -> AppConfig:
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")

    if not base_url or not api_key:
        raise ValueError("BASE_URL and API_KEY must be set in.env")

    return AppConfig(base_url=base_url.rstrip("/"), api_key=api_key)
