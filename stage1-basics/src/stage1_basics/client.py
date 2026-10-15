from __future__ import annotations

import asyncio
import time
from typing import Any

import httpx

from stage1_basics.cache import TTLCache
from stage1_basics.config import AppConfig, load_config
from stage1_basics.errors import ApiError, AuthError, NotFoundError, ServerError
from stage1_basics.http import CircuitBreaker, RetryPolicy, exponential_backoff

SEMAPHORE = asyncio.Semaphore(3)
CACHE = TTLCache(ttl=300.0)
_PENDING: dict[str, asyncio.Future[dict[str, Any]]] = {}

RETRY_POLICY = RetryPolicy(max_retries=3, base_delay=0.2, max_delay=5.0)
CIRCUIT = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)


async def fetch(
    client: httpx.AsyncClient,
    cfg: AppConfig,
    path: str,
    retries: int | None = None,
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

    if not CIRCUIT.can_execute():
        err = ApiError(f"Circuit {CIRCUIT.state.value} open - fail fast: {url}")
        future.set_exception(err)
        raise err

    headers = {
        "Authorization": f"Bearer {cfg.api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(10.0)
    last_exc: Exception | None = None
    policy = RETRY_POLICY
    max_attempts = retries if retries is not None else policy.max_retries

    try:
        async with SEMAPHORE:
            for attempt in range(max_attempts):
                try:
                    start = time.perf_counter()
                    resp = await client.get(url, headers=headers, timeout=timeout)
                    elapsed = time.perf_counter() - start

                    if resp.status_code == 401:
                        raise AuthError(f"401 Unauthorized: {url} ({elapsed:.2f}s)")
                    if resp.status_code == 404:
                        raise NotFoundError(f"404 Not Found: {url} ({elapsed:.2f}s)")
                    if resp.status_code in policy.retry_on:
                        raise ServerError(f"{resp.status_code} Retryable: {url}")

                    resp.raise_for_status()
                    result: dict[str, Any] = {
                        "url": str(resp.url),
                        "status": resp.status_code,
                        "elapsed": elapsed,
                        "data": resp.json(),
                        "cached": False,
                        "retries": attempt,
                        "circuit": CIRCUIT.state.value,
                    }
                    if use_cache:
                        CACHE.set(cache_key, result)

                    CIRCUIT.record_success()
                    future.set_result(result)
                    return result

                except (ServerError, httpx.RequestError, httpx.HTTPStatusError) as exc:
                    last_exc = exc
                    CIRCUIT.record_failure()
                    if attempt == max_attempts - 1:
                        break
                    delay = exponential_backoff(
                        attempt, policy.base_delay, policy.max_delay, policy.jitter
                    )
                    await asyncio.sleep(delay)

        err = ApiError(f"Failed after {max_attempts} retries: {url}")
        err.__cause__ = last_exc
        future.set_exception(err)
        raise err

    finally:
        _PENDING.pop(cache_key, None)


async def main() -> None:
    cfg = load_config()
    print(f"Using BASE_URL: {cfg.base_url} | Conc: 3 | TTL: {CACHE.ttl}s")
    print(f"Cache path: {CACHE.persist_path} | Exists: {CACHE.persist_path.exists()}")
    print(f"Circuit: {CIRCUIT.state.value} | Retries: {RETRY_POLICY.max_retries}")

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
        results = await asyncio.gather(
            *[fetch(client, cfg, "/get?day12=coalesce") for _ in range(5)],
            return_exceptions=True,
        )
        ok = sum(1 for r in results if isinstance(r, dict))
        print(
            f"5 concurrent -> ok={ok} calls={CACHE.metrics.network_calls} "
            f"coalesced={CACHE.metrics.coalesced} circuit={CIRCUIT.state.value}"
        )
    print(f"Final metrics: {CACHE.metrics.to_dict()}")


if __name__ == "__main__":
    asyncio.run(main())
