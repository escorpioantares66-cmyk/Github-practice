from __future__ import annotations

import asyncio
from typing import Any

import httpx

from stage1_basics.config import AppConfig, load_config


async def fetch(client: httpx.AsyncClient, cfg: AppConfig, path: str) -> dict[str, Any]:
    url = f"{cfg.base_url}{path}"
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(10.0)
    resp = await client.get(url, headers=headers, timeout=timeout)
    resp.raise_for_status()
    return {
        "url": str(resp.url),
        "status": resp.status_code,
        "data": resp.json(),
    }


async def main() -> None:
    cfg = load_config()
    print(f"Using BASE_URL: {cfg.base_url}")
    async with httpx.AsyncClient() as client:
        results = await asyncio.gather(
            fetch(client, cfg, "/get?test=1"),
            fetch(client, cfg, "/get?test=2"),
            fetch(client, cfg, "/get?test=3"),
        )
    for r in results:
        print(r["status"], r["url"])


if __name__ == "__main__":
    asyncio.run(main())
