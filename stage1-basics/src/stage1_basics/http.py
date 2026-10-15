from __future__ import annotations

import asyncio
import random
import time
from dataclasses import dataclass, field
from enum import Enum


class CircuitState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryPolicy:
    max_retries: int = 3
    base_delay: float = 0.2
    max_delay: float = 5.0
    jitter: bool = True
    retry_on: tuple[int, ...] = (429, 500, 502, 503, 504)


@dataclass
class CircuitBreaker:
    failure_threshold: int = 3
    recovery_timeout: float = 30.0
    state: CircuitState = CircuitState.CLOSED
    failure_count: int = 0
    last_failure_time: float | None = None
    _half_open_trial: bool = field(default=False, init=False)

    def can_execute(self) -> bool:
        if self.state == CircuitState.CLOSED:
            return True
        if self.state == CircuitState.OPEN:
            if self.last_failure_time is None:
                return False
            elapsed = time.monotonic() - self.last_failure_time
            if elapsed >= self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self._half_open_trial = False
                return True
            return False
        return not self._half_open_trial

    def record_success(self) -> None:
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
        self._half_open_trial = False

    def record_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.monotonic()
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            self._half_open_trial = True
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN


def exponential_backoff(
    attempt: int, base: float, max_delay: float, jitter: bool
) -> float:
    delay = base * (2**attempt)
    if jitter:
        delay = delay + random.uniform(0, base)
    return min(delay, max_delay)


async def sleep_backoff(attempt: int, policy: RetryPolicy) -> None:
    d = exponential_backoff(attempt, policy.base_delay, policy.max_delay, policy.jitter)
    await asyncio.sleep(d)


async def should_retry(
    status_code: int | None, exc: Exception | None, policy: RetryPolicy
) -> bool:
    if exc is not None:
        return True
    if status_code is None:
        return True
    return status_code in policy.retry_on
