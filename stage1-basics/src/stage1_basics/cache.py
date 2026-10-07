import asyncio
import json
import time
from collections import OrderedDict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional


@dataclass
class CacheMetrics:
    hits: int = 0
    misses: int = 0
    network_calls: int = 0
    coalesced: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total else 0.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": round(self.hit_rate, 1),
            "network_calls": self.network_calls,
            "coalesced": self.coalesced,
        }

    def reset(self) -> None:
        self.hits = 0
        self.misses = 0
        self.network_calls = 0
        self.coalesced = 0


class TTLCache:
    def __init__(
        self,
        cache_dir: str = ".cache",
        ttl: float = 300,
        maxsize: int = 128,
        persist_path: Optional[Path] = None,
    ):
        if persist_path is not None:
            pp = Path(persist_path)
            self.persist_path = pp
            self.cache_dir = pp.parent
        else:
            self.cache_dir = Path(cache_dir)
            self.persist_path = self.cache_dir / "cache.json"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = float(ttl)
        self.maxsize = int(maxsize)
        self._cache: OrderedDict[str, Dict[str, Any]] = OrderedDict()
        self.metrics = CacheMetrics()
        self._locks: Dict[str, asyncio.Lock] = {}
        self._global_lock = asyncio.Lock()
        self._load()

    def _load(self) -> None:
        if not self.persist_path.exists():
            return
        try:
            data = json.loads(self.persist_path.read_text())
            for k, v in data.items():
                self._cache[k] = v
        except Exception:
            self._cache = OrderedDict()

    def _persist(self) -> None:
        try:
            self.persist_path.write_text(json.dumps(dict(self._cache), indent=2))
        except Exception:
            pass

    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        return (time.time() - entry.get("ts", 0)) > self.ttl

    def get(self, key: str) -> Optional[Any]:
        entry = self._cache.get(key)
        if not entry:
            self.metrics.misses += 1
            return None
        if self._is_expired(entry):
            self.invalidate(key)
            self.metrics.misses += 1
            return None
        self._cache.move_to_end(key)
        self._persist()
        self.metrics.hits += 1
        return entry.get("value")

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = {"value": value, "ts": time.time()}
        self._cache.move_to_end(key)
        while len(self._cache) > self.maxsize:
            self._cache.popitem(last=False)
        self._persist()

    def invalidate(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            self._persist()
            return True
        return False

    def clear(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        self._persist()
        return count

    def reset_metrics(self) -> None:
        self.metrics.reset()

    def metrics_dict(self) -> Dict[str, Any]:
        return self.metrics.to_dict()

    def __len__(self) -> int:
        return len(self._cache)

    def __contains__(self, key: object) -> bool:
        return key in self._cache


PersistentCache = TTLCache
CACHE = TTLCache()
