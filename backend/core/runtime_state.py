import time
from collections import defaultdict


class InMemoryRateLimiter:
    def __init__(self, limit: int, window_sec: int):
        self.limit = limit
        self.window_sec = window_sec
        self.buckets: dict[str, list[float]] = defaultdict(list)

    def allow(self, key: str) -> bool:
        now = time.time()
        bucket = [t for t in self.buckets[key] if now - t < self.window_sec]
        self.buckets[key] = bucket
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True
