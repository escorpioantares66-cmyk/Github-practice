from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class CacheEntry:
    data: dict[str, Any]
    expires_at: float


@dataclass(slots=True)
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    coalesced: int = 0
    network_calls: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total else 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "coalesced": self.coalesced,
            "network_calls": self.network_calls,
            "hit_rate": f"{self.hit_rate:.1f}%",
        }


class TTLCache:
    def __init__(self, ttl: float = 60.0, persist_path: Path | None = None) -> None:
        self.ttl = ttl
        self.persist_path = persist_path or Path(".cache/http_cache.json")
        self._store: dict[str, CacheEntry] = {}
        self.metrics = CacheMetrics()
        self.load()

    def get(self, key: str) -> dict[str, Any] | None:
        entry = self._store.get(key)
        if not entry:
            self.metrics.misses += 1
            return None
        if time.monotonic() > entry.expires_at:
            del self._store[key]
            self.metrics.misses += 1
            return None
        self.metrics.hits += 1
        return entry.data

    def set(self, key: str, data: dict[str, Any]) -> None:
        self._store[key] = CacheEntry(
            data=data,
            expires_at=time.monotonic() + self.ttl,
        )
        self.metrics.network_calls += 1
        self.save()

    def clear(self) -> None:
        self._store.clear()
        self.metrics = CacheMetrics()
        if self.persist_path.exists():
            self.persist_path.unlink(missing_ok=True)

    def save(self) -> None:
        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            serializable = {
                k: {"data": v.data, "expires_at": v.expires_at}
                for k, v in self._store.items()
                if time.monotonic() <= v.expires_at
            }
            self.persist_path.write_text(json.dumps(serializable, indent=2))
        except Exception:
            pass

    def load(self) -> None:
        try:
            if not self.persist_path.exists():
                return
            raw = json.loads(self.persist_path.read_text())
            now = time.monotonic()
            for k, v in raw.items():
                if v["expires_at"] > now:
                    self._store[k] = CacheEntry(
                        data=v["data"], expires_at=v["expires_at"]
                    )
        except Exception:
            pass

    def __len__(self) -> int:
        return len(self._store)
