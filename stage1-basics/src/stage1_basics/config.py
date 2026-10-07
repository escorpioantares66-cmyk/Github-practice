import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

@dataclass
class AppConfig:
    base_url: str
    api_key: str
    headers: dict[str, str] = field(
        default_factory=lambda: {
            "Content-Type": "application/json"
        }
    )

    @classmethod
    def from_env(cls) -> "AppConfig":
        base_url = os.getenv("BASE_URL")
        api_key = os.getenv("API_KEY")
        if not base_url or not api_key:
            raise ValueError("Missing BASE_URL or API_KEY in .env")
        return cls(base_url=base_url, api_key=api_key)

    def load_json_config(self, path: Path | str) -> dict[str, Any]:
        p = Path(path)
        if not p.exists():
            raise FileNotFoundError(f"Config not found: {p}")
        return json.loads(p.read_text())

    def save_json_config(
        self, path: Path | str, data: dict[str, Any]
    ) -> None:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data, indent=2))
