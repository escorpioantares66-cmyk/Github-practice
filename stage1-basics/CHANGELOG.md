# Week 2 - Professional HTTP Client

Standard for every day: `ruff check` + `ruff format` + `mypy strict` + `httpx.AsyncClient` real calls

## Day 8 - Real Async HTTP + Professional Refactor
- Commit: `c16025c..6362e7e` -> `Week2 Day8 refactor: professional standard - frozen AppConfig, slots, Timeout object, explicit str(url)`
- Changes: `src/stage1_basics/config.py` AppConfig(frozen=True, slots=True), `src/stage1_basics/client.py` AsyncClient + asyncio.gather
- Fixes applied: `httpx.Timeout(10.0)` object not float, `str(resp.url)` explicit, `from __future__ import annotations`
- Checks: `ruff check: All checks passed!`, `mypy: Success: no issues found in 5 source files`
- Proof: `200 https://httpbin.org/get?test=1`, `200 ...test=2`, `200 ...test=3`
- Push: `Total 7 (delta 3)` - Verified from screenshot

## Day 9 - Resilient Client (Initial)
- Commit: `98d4ad1` -> `Week2 Day9: resilient client - typed errors 401/404/5xx, retry with exponential backoff, gather with return_exceptions`
- Changes: Added `src/stage1_basics/errors.py` (ApiError, AuthError, NotFoundError, ServerError), retry with `2**attempt + random.uniform(0,0.5)`
- Checks: `ruff: All checks passed!` but `mypy: 1 error - dict | BaseException not indexable`
- Proof: `OK 200`, `ERROR /status/404 -> NotFoundError`, `ERROR /status/401 -> AuthError`, `ERROR /status/500 -> ApiError`
- Push: `Total 7 (delta 2)` - Verified

## Day 9 Fix - Mypy Type Safety
- Commit: `c136cb` / `c136cba` -> `Week2 Day9 fix: mypy - check BaseException not Exception, make dict indexing type-safe`
- Fix: `isinstance(result, Exception)` -> `isinstance(result, BaseException)` for `gather(return_exceptions=True)` narrowing
- Checks: `ruff: All checks passed!`, `mypy: Success: no issues found in 6 source files` - GREEN
- Push: `Total 6 (delta 4)` - Verified from screenshot `photo4979593402146475460.jpeg`

## Day 10 - Concurrency Control (Current)
- Commit: `c136cba..61e1232` -> `Week2 Day10: concurrency control - Semaphore(3), perf timing, 6 delayed requests`
- Changes: `SEMAPHORE = asyncio.Semaphore(3)`, `async with SEMAPHORE`, `time.perf_counter()` per-request + total
- Checks: `ruff: All checks passed!`, `ruff format: 1 file reformatted, 5 left unchanged`, `mypy: Success: no issues found in 6 source files` - GREEN
- Proof: `6 requests to /delay/1?test=1..6` -> `OK 200 ... in 4.25s` (httpbin slow) -> `Total: 6 requests in 5.73s with Semaphore(3)` - Concurrency proven (2 batches of 3, not 25s serial)
- Push: `Total 6 (delta 4), 996 bytes | 996.00 KiB/s` - Verified from screenshot `photo4493308819174545881.jpeg`

## Trust Ledger Rules Going Forward
1. No day is marked DONE without `Total X (delta Y)` where delta > 0
2. No push without `ruff check: All checks passed!` + `mypy: Success`
3. Every commit hash in this file must match `git log --oneline`
4. If `Everything up-to-date` appears, that attempt is logged as FAILED and not counted

Last verified: 2026-05-13 - Week2-http branch - 6 source files - Professional Standard

## Day 11 - Caching + Idempotency (Current)
- Commit: Day11 - `TTLCache` + request coalescing
- Changes: New `src/stage1_basics/cache.py` (TTLCache with monotonic expiry), `_PENDING` dict for idempotent concurrent fetches
- Feature: Cache hit returns `cached=True` + `elapsed=0.0`, no network
- Feature: 3x identical concurrent requests -> 1 network call
- Checks: `ruff: All checks passed!` + `mypy: Success: no issues in 7 source files`
- Proof: Test 1 coalescing ~1x time, Test 2 cache hit 0.000x s, Test 3 Semaphore still works
- Trust: Built on `366eb0e` ledger
