import os
from pathlib import Path
from dotenv import load_dotenv

def load_config() -> dict[str, str]:
    # Load.env from project root
    env_path = Path(__file__).resolve().parents[2] / ".env"
    load_dotenv(dotenv_path=env_path, override=True)

    base_url = os.getenv("BASE_URL")
    api_key = os.getenv("API_KEY")

    if not base_url or not api_key:
        raise ValueError("BASE_URL and API_KEY must be set in.env")

    return {"BASE_URL": base_url, "API_KEY": api_key}
