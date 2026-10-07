from __future__ import annotations

import asyncio
import random
from typing import Any

import httpx

from stage1_basics.config import AppConfig, load_config
from stage1_basics.errors import ApiError, AuthError, NotFoundError, ServerError


async def fetch(
    client: httpx.AsyncClient,
    cfg: AppConfig,
    path: str,
    retries: int = 3,
) -> dict[str, Any]:
    url = f"{cfg.base_url}{path}"
    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(10.0)

    last_exc: Exception | None = None

    for attempt in range(retries):
        try:
            resp = await client.get(url, headers=headers, timeout=timeout)

            if resp.status_code == 401:
                raise AuthError(f"401 Unauthorized: {url}")
            if resp.status_code == 404:
                raise NotFoundError(f"404 Not Found: {url}")
            if resp.status_code == 429 or 500 <= resp.status_code < 600:
                raise ServerError(f"{resp.status_code} Retryable: {url}")

            resp.raise_for_status()
            return {
                "url": str(resp.url),
                "status": resp.status_code,
                "data": resp.json(),
            }

        except (ServerError, httpx.RequestError, httpx.HTTPStatusError) as exc:
            last_exc = exc
            if attempt == retries - 1:
                break
            backoff = (2**attempt) + random.uniform(0, 0.5)
            await asyncio.sleep(backoff)

    raise ApiError(f"Failed after {retries} retries: {url}") from last_exc


async def main() -> None:
    cfg = load_config()
    print(f"Using BASE_URL: {cfg.base_url}")

    paths = [
        "/get?test=1",
        "/status/404",
        "/status/401",
        "/status/500",
        "/get?test=2",
    ]

    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, cfg, p, retries=2) for p in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)

    for path, result in zip(paths, results, strict=True):
        if isinstance(result, Exception):
            print(f"ERROR {path} -> {type(result).__name__}: {result}")
        else:
            print(f"OK {result['status']} {result['url']}")


if __name__ == "__main__":
    asyncio.run(main())
