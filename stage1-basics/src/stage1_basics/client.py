import asyncio
from typing import Any

import httpx

from stage1_basics.config import AppConfig

class APIClient:
    """Async client that talks to external APIs without blocking."""

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._client = httpx.AsyncClient(
            base_url=config.base_url,
            headers=config.headers,
        )

    def _build_url(self, endpoint: str) -> str:
        return f"{self.config.base_url}{endpoint}"

    @property
    def auth_header(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.config.api_key}"}

    async def get(self, endpoint: str) -> dict[str, Any]:
        url = self._build_url(endpoint)
        await asyncio.sleep(1)
        return {"url": url, "headers": {**self.config.headers, **self.auth_header}}

    async def close(self) -> None:
        await self._client.aclose()
