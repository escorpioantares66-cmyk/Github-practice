from __future__ import annotations

import asyncio
import random
import time
from typing import Any

import httpx

from stage1_basics.cache import TTLCache
from stage1_basics.config import AppConfig, load_config
from stage1_basics.errors import ApiError, AuthError, NotFoundError, ServerError

SEMAPHORE = asyncio.Semaphore(3)
CACHE = TTLCache(ttl=300.0)
_PENDING: dict[str, asyncio.Future[dict[str, Any]]] = {}


async def fetch(
    client: httpx.AsyncClient,
    cfg: AppConfig,
    path: str,
    retries: int = 3,
    use_cache: bool = True,
) -> dict[str, Any]:
    url = f"{cfg.base_url}{path}"
    cache_key = url

    if use_cache:
        cached = CACHE.get(cache_key)
        if cached is not None:
            return {**cached, "cached": True, "elapsed": 0.0}

    if cache_key in _PENDING:
        CACHE.metrics.coalesced += 1
        return await _PENDING[cache_key]

    loop = asyncio.get_running_loop()
    future: asyncio.Future[dict[str, Any]] = loop.create_future()
    _PENDING[cache_key] = future

    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(10.0)
    last_exc: Exception | None = None

    try:
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
                    result: dict[str, Any] = {
                        "url": str(resp.url),
                        "status": resp.status_code,
                        "elapsed": elapsed,
                        "data": resp.json(),
                        "cached": False,
                    }
                    if use_cache:
                        CACHE.set(cache_key, result)
                    future.set_result(result)
                    return result

                except (ServerError, httpx.RequestError, httpx.HTTPStatusError) as exc:
                    last_exc = exc
                    if attempt == retries - 1:
                        break
                    backoff = (2**attempt) + random.uniform(0, 0.5)
                    await asyncio.sleep(backoff)

        err = ApiError(f"Failed after {retries} retries: {url}")
        err.__cause__ = last_exc
        future.set_exception(err)
        raise err

    finally:
        _PENDING.pop(cache_key, None)


async def main() -> None:
    cfg = load_config()
    print(f"Using BASE_URL: {cfg.base_url} | Concurrency: 3 | TTL: {CACHE.ttl}s")
    print(f"Cache path: {CACHE.persist_path} | Exists: {CACHE.persist_path.exists()}")

    print("\n--- Test 1: Populate cache (network) ---")
    CACHE.clear()
    async with httpx.AsyncClient() as client:
        r1 = await fetch(client, cfg, "/get?day12=1")
    print(f"OK {r1['status']} cached={r1['cached']} | Cache size: {len(CACHE)}")
    print(f"Metrics: {CACHE.metrics.to_dict()}")
    print(f"Disk cache written: {CACHE.persist_path.exists()}")

    print("\n--- Test 2: Memory hit ---")
    async with httpx.AsyncClient() as client:
        r2 = await fetch(client, cfg, "/get?day12=1")
    print(f"OK {r2['status']} cached={r2['cached']} in {r2['elapsed']:.4f}s")
    print(f"Metrics: {CACHE.metrics.to_dict()}")

    print("\n--- Test 3: Persistent hit after 'restart' ---")
    new_cache = TTLCache(ttl=300.0, persist_path=CACHE.persist_path)
    print(f"New instance loaded {len(new_cache)} entries from disk")
    cached = new_cache.get("https://httpbin.org/get?day12=1")
    print(f"Disk hit: {cached is not None} | Rate: {new_cache.metrics.hit_rate:.1f}%")

    print("\n--- Test 4: Coalescing + full metrics ---")
    CACHE.clear()
    async with httpx.AsyncClient() as client:
        await asyncio.gather(
            *[fetch(client, cfg, "/get?day12=coalesce") for _ in range(5)],
            return_exceptions=True,
        )
        print(
            f"5 concurrent -> calls={CACHE.metrics.network_calls}, "
            f"coalesced={CACHE.metrics.coalesced}"
        )
    print(f"Final metrics: {CACHE.metrics.to_dict()}")


if __name__ == "__main__":
    asyncio.run(main())
