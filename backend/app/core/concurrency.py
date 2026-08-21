import threading
from contextlib import contextmanager


class CrawlConcurrencyManager:
    def __init__(self, max_concurrent: int):
        self.max_concurrent = max_concurrent
        self._active = 0
        self._lock = threading.Lock()

    def can_start(self) -> bool:
        with self._lock:
            return self._active < self.max_concurrent

    @contextmanager
    def acquire(self):
        with self._lock:
            self._active += 1
        try:
            yield
        finally:
            with self._lock:
                self._active -= 1

concurrency_manager = CrawlConcurrencyManager(max_concurrent=5)
