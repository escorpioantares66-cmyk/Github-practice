from __future__ import annotations

import asyncio
import random
import time
from typing import Any

import httpx

from stage1_basics.config import AppConfig, load_config
from stage1_basics.errors import ApiError, AuthError, NotFoundError, ServerError

SEMAPHORE = asyncio.Semaphore(3)


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

    async with SEMAPHORE:
        for attempt in range(retries):
            try:
                start = time.perf_counter()
                resp = await client.get(url, headers=headers, timeout=timeout)
                elapsed = time.perf_counter() - start

                if resp.status_code == 401:
                    raise AuthError(f"401 Unauthorized: {url} ({elapsed:.2f}s)")
                if resp.status_code == 404:
                    raise NotFoundError(f"404 Not Found: {url} ({elapsed:.2f}s)")
                if resp.status_code == 429 or 500 <= resp.status_code < 600:
                    raise ServerError(f"{resp.status_code} Retryable: {url}")

                resp.raise_for_status()
                return {
                    "url": str(resp.url),
                    "status": resp.status_code,
                    "elapsed": elapsed,
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
    print(f"Using BASE_URL: {cfg.base_url} | Concurrency: 3")

    paths = [f"/delay/1?test={i}" for i in range(1, 7)]

    overall_start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, cfg, p, retries=2) for p in paths]
        results = await asyncio.gather(*tasks, return_exceptions=True)
    overall_elapsed = time.perf_counter() - overall_start

    for path, result in zip(paths, results, strict=True):
        if isinstance(result, BaseException):
            print(f"ERROR {path} -> {type(result).__name__}: {result}")
        else:
            print(f"OK {result['status']} {result['url']} in {result['elapsed']:.2f}s")

    print(f"\nTotal: {len(paths)} requests in {overall_elapsed:.2f}s with Semaphore(3)")


if __name__ == "__main__":
    asyncio.run(main())
