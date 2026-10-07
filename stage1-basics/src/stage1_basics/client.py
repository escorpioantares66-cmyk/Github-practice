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
CACHE = TTLCache(ttl=60.0)
# For idempotency: if same URL is already being fetched, others wait for it
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

    # Idempotency / coalescing
    if cache_key in _PENDING:
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
    print(f"Using BASE_URL: {cfg.base_url} | Concurrency: 3 | Cache TTL: {CACHE.ttl}s")

    # 1. Test coalescing - 3 identical requests at same time should do 1 network call
    print("\n--- Test 1: Request Coalescing (3x same URL concurrently) ---")
    CACHE.clear()
    paths_same = ["/get?cache=test" for _ in range(3)]
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        results = await asyncio.gather(
            *[fetch(client, cfg, p) for p in paths_same], return_exceptions=True
        )
        elapsed_same = time.perf_counter() - start

    for r in results:
        if isinstance(r, BaseException):
            print(f"ERROR -> {r}")
        else:
            print(f"OK {r['status']} cached={r['cached']} in {r['elapsed']:.2f}s")
    print(
        f"3 identical concurrent requests finished in {elapsed_same:.2f}s (should be ~1x network time)"
    )

    # 2. Test cache hit - second call should be instant
    print("\n--- Test 2: Cache Hit (same URL again) ---")
    async with httpx.AsyncClient() as client:
        start = time.perf_counter()
        result_cached = await fetch(client, cfg, "/get?cache=test")
        elapsed_cached = time.perf_counter() - start
    print(
        f"OK {result_cached['status']} cached={result_cached['cached']} in {elapsed_cached:.4f}s"
    )
    print(f"Cache size: {len(CACHE)} entry")

    # 3. Test normal concurrent with semaphore still works
    print("\n--- Test 3: Normal concurrent (6x delay/1) with cache disabled ---")
    CACHE.clear()
    paths_delay = [f"/delay/1?test={i}" for i in range(1, 7)]
    overall_start = time.perf_counter()
    async with httpx.AsyncClient() as client:
        tasks = [fetch(client, cfg, p, use_cache=False) for p in paths_delay]
        results_delay = await asyncio.gather(*tasks, return_exceptions=True)
    overall = time.perf_counter() - overall_start
    for p, r in zip(paths_delay, results_delay, strict=True):
        if isinstance(r, BaseException):
            print(f"ERROR {p} -> {type(r).__name__}: {r}")
        else:
            print(f"OK {r['status']} {r['url']} in {r['elapsed']:.2f}s")
    print(f"Total: {len(paths_delay)} requests in {overall:.2f}s with Semaphore(3)")


if __name__ == "__main__":
    asyncio.run(main())
