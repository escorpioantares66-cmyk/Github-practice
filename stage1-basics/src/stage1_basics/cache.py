from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class CacheEntry:
    data: dict[str, Any]
    expires_at: float


class TTLCache:
    def __init__(self, ttl: float = 60.0) -> None:
        self.ttl = ttl
        self._store: dict[str, CacheEntry] = {}

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._store.get(key)
        if not entry:
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            return None
        return entry.data

    def set(self, key: str, data: dict[str, Any]) -> None:
        self._store[key] = CacheEntry(
            data=data,
            expires_at=time.monotonic() + self.ttl,
        )

    def clear(self) -> None:
        self._store.clear()

    def __len__(self) -> int:
        return len(self._store)
