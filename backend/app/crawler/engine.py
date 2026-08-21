import asyncio
import time
from dataclasses import dataclass, field

from app.core.config import settings
from app.crawler.audit import SEOAuditEngine
from app.crawler.client import AsyncCrawlerClient
from app.crawler.health import LinkHealthAnalyzer
from app.crawler.parser import HTMLParser
from app.crawler.url import (
    URLTracker,
    is_same_domain,
    is_valid_url,
    normalize_url,
    resolve_url,
)
from app.schemas.report import (
    CrawlReportSchema,
    CrawlStatsSchema,
    HealthIssueSchema,
    PageReportSchema,
    SEOIssueSchema,
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
        check_external_links: bool = False,
    ):
        self.start_url = normalize_url(start_url)
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.max_concurrency = max_concurrency
        self.check_external_links = check_external_links

        self.tracker = URLTracker()
        self.client = AsyncCrawlerClient(max_connections=max_concurrency)
        self.stats = CrawlStats()
        self.health_analyzer = LinkHealthAnalyzer()
        self.audit_engine = SEOAuditEngine()
        self.pages_data: dict[str, PageReportSchema] = {}

        self.queue: asyncio.Queue[tuple[str, int, bool]] = asyncio.Queue()
        self.active_tasks = 0
        self._stop_event = asyncio.Event()
        self._processed_count = 0

    async def _worker(self):
        while not self._stop_event.is_set():
            try:
                # Use a small timeout so the worker checks the stop_event and shutdown conditions frequently
                url, depth, is_external = await asyncio.wait_for(self.queue.get(), timeout=0.5)
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
                
                self.health_analyzer.record_visit(
                    url=url,
                    status_code=result.status_code,
                    error_type=result.error_type,
                    redirect_target=result.redirect_url
                )

                if result.error_type or (result.status_code and result.status_code >= 400):
                    self.stats.pages_failed += 1
                else:
                    self.stats.pages_crawled += 1

                    # Skip parsing for external links
                    if is_external:
                        continue

                    # Discover new links using the dedicated parser
                    if result.html_content and depth < self.max_depth:
                        parsed = HTMLParser(result.html_content, url).parse()
                        
                        # Run SEO audit
                        audit_issues = self.audit_engine.run_audit(url, parsed)
                        seo_issues_schemas = [
                            SEOIssueSchema(
                                rule_id=i.rule_id,
                                severity=i.severity,
                                message=i.message,
                                element=i.element,
                            )
                            for i in audit_issues
                        ]
                        
                        # Build internal links list for the report
                        internal_links = [
                            link.href for link in parsed.links if is_same_domain(self.start_url, link.href)
                        ]
                        
                        # Store page data
                        self.pages_data[url] = PageReportSchema(
                            url=url,
                            status_code=result.status_code,
                            title=parsed.title,
                            meta_description=parsed.meta_description,
                            canonical_url=parsed.canonical_url,
                            language=parsed.language,
                            robots_meta=parsed.robots_meta,
                            h1_tags=parsed.h1_tags,
                            h2_tags=parsed.h2_tags,
                            h3_tags=parsed.h3_tags,
                            internal_links=internal_links,
                            seo_issues=seo_issues_schemas,
                        )
                        
                        # Record links for health analysis
                        self.health_analyzer.record_links(url, {link.href for link in parsed.links})
                        
                        for link_info in parsed.links:
                            if is_same_domain(self.start_url, link_info.href):
                                if not self.tracker.is_visited(link_info.href):
                                    self.tracker.mark_visited(link_info.href)
                                    await self.queue.put((link_info.href, depth + 1, False))
                            elif self.check_external_links and not self.tracker.is_visited(link_info.href):
                                self.tracker.mark_visited(link_info.href)
                                # External links don't increase depth and won't be parsed
                                await self.queue.put((link_info.href, depth, True))

                    # Follow internal redirects (or external if tracking them)
                    if result.redirect_url:
                        resolved_redirect = resolve_url(url, result.redirect_url)
                        if is_valid_url(resolved_redirect) and not self.tracker.is_visited(resolved_redirect):
                            if is_same_domain(self.start_url, resolved_redirect):
                                self.tracker.mark_visited(resolved_redirect)
                                await self.queue.put((resolved_redirect, depth, False))
                            elif self.check_external_links:
                                self.tracker.mark_visited(resolved_redirect)
                                await self.queue.put((resolved_redirect, depth, True))
            except Exception:  # noqa: BLE001
                # Fail-safe to ensure crawler doesn't completely crash on unexpected worker errors
                self.stats.pages_failed += 1
            finally:
                self.queue.task_done()
                self.active_tasks -= 1

    async def run(self) -> CrawlReportSchema:
        """
        Start the crawl engine and block until finished.
        """
        self.stats.start_time = time.monotonic()
        self.tracker.mark_visited(self.start_url)
        await self.queue.put((self.start_url, 0, False))

        workers = [asyncio.create_task(self._worker()) for _ in range(self.max_concurrency)]

        # Wait for all workers to complete
        await asyncio.gather(*workers)

        self.stats.end_time = time.monotonic()
        await self.client.close()
        
        # Build health issues schema
        health_issues_raw = self.health_analyzer.analyze()
        health_issues = [
            HealthIssueSchema(
                url=h.url,
                issue_type=h.issue_type,
                description=h.description,
            )
            for h in health_issues_raw
        ]
        
        # Build final report
        stats_schema = CrawlStatsSchema(
            pages_crawled=self.stats.pages_crawled,
            pages_failed=self.stats.pages_failed,
            duration_seconds=self.stats.duration,
        )
        
        report = CrawlReportSchema(
            start_url=self.start_url,
            stats=stats_schema,
            pages=list(self.pages_data.values()),
            health_issues=health_issues,
        )
        
        return report
