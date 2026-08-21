import asyncio
import time
from dataclasses import dataclass, field

from bs4 import BeautifulSoup

from app.core.config import settings
from app.crawler.client import AsyncCrawlerClient
from app.crawler.url import (
    URLTracker,
    is_same_domain,
    is_valid_url,
    normalize_url,
    resolve_url,
)


@dataclass
class CrawlStats:
    pages_crawled: int = 0
    pages_failed: int = 0
    start_time: float = field(default_factory=time.monotonic)
    end_time: float | None = None

    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.monotonic() - self.start_time


class CrawlerEngine:
    """
    Core orchestration engine for crawling a website.
    """

    def __init__(
        self,
        start_url: str,
        max_pages: int = 50,
        max_depth: int = 3,
        max_concurrency: int = settings.MAX_CONCURRENCY,
    ):
        self.start_url = normalize_url(start_url)
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.max_concurrency = max_concurrency

        self.tracker = URLTracker()
        self.client = AsyncCrawlerClient(max_connections=max_concurrency)
        self.stats = CrawlStats()

        self.queue: asyncio.Queue[tuple[str, int]] = asyncio.Queue()
        self.active_tasks = 0
        self._stop_event = asyncio.Event()
        self._processed_count = 0

    def _extract_links(self, html: str, base_url: str) -> set[str]:
        """
        Minimal link extraction for internal link discovery.
        (Will be expanded into a dedicated parser in future milestones).
        """
        soup = BeautifulSoup(html, "html.parser")
        links = set()
        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            resolved = resolve_url(base_url, href)
            # Only keep valid, internal links
            if is_valid_url(resolved) and is_same_domain(self.start_url, resolved):
                links.add(resolved)
        return links

    async def _worker(self):
        while not self._stop_event.is_set():
            try:
                # Use a small timeout so the worker checks the stop_event and shutdown conditions frequently
                url, depth = await asyncio.wait_for(self.queue.get(), timeout=0.5)
            except TimeoutError:
                # If queue is empty and no active tasks are fetching, we are completely done
                if self.active_tasks == 0 and self.queue.empty():
                    break
                continue

            self.active_tasks += 1
            try:
                # Strictly respect max_pages
                if self._processed_count >= self.max_pages:
                    self._stop_event.set()
                    continue

                if depth > self.max_depth:
                    continue

                self._processed_count += 1
                result = await self.client.fetch(url)

                if result.error_type or (result.status_code and result.status_code >= 400):
                    self.stats.pages_failed += 1
                else:
                    self.stats.pages_crawled += 1

                    # Discover new links
                    if result.html_content and depth < self.max_depth:
                        links = self._extract_links(result.html_content, url)
                        for link in links:
                            if not self.tracker.is_visited(link):
                                self.tracker.mark_visited(link)
                                await self.queue.put((link, depth + 1))

                    # Follow internal redirects
                    if result.redirect_url:
                        resolved_redirect = resolve_url(url, result.redirect_url)
                        if (
                            is_valid_url(resolved_redirect)
                            and is_same_domain(self.start_url, resolved_redirect)
                            and not self.tracker.is_visited(resolved_redirect)
                        ):
                            self.tracker.mark_visited(resolved_redirect)
                            await self.queue.put((resolved_redirect, depth))
            except Exception:  # noqa: BLE001
                # Fail-safe to ensure crawler doesn't completely crash on unexpected worker errors
                self.stats.pages_failed += 1
            finally:
                self.queue.task_done()
                self.active_tasks -= 1

    async def run(self) -> CrawlStats:
        """
        Start the crawl engine and block until finished.
        """
        self.stats.start_time = time.monotonic()
        self.tracker.mark_visited(self.start_url)
        await self.queue.put((self.start_url, 0))

        workers = [asyncio.create_task(self._worker()) for _ in range(self.max_concurrency)]

        # Wait for all workers to complete
        await asyncio.gather(*workers)

        self.stats.end_time = time.monotonic()
        await self.client.close()
        return self.stats
