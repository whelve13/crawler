from unittest.mock import AsyncMock, patch

import pytest

from app.crawler.client import FetchResult
from app.crawler.engine import CrawlerEngine


@pytest.fixture
def mock_client():
    with patch("app.crawler.engine.AsyncCrawlerClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.close = AsyncMock()
        
        # Simple router to simulate a small website
        async def mock_fetch(url: str, *args, **kwargs):
            if url == "https://example.com":
                return FetchResult(
                    url=url,
                    status_code=200,
                    html_content='<a href="/page1">Page 1</a><a href="/page2">Page 2</a>',
                )
            elif url == "https://example.com/page1":
                return FetchResult(
                    url=url,
                    status_code=200,
                    html_content='<a href="/page2">Page 2</a><a href="https://external.com">External</a>',
                )
            elif url == "https://example.com/page2":
                return FetchResult(
                    url=url,
                    status_code=404,
                    error_type="HTTP_404",
                )
            elif url == "https://example.com/redirect":
                return FetchResult(
                    url=url,
                    status_code=301,
                    redirect_url="/page1",
                )
            return FetchResult(url=url, status_code=500, error_type="HTTP_500")

        mock_instance.fetch.side_effect = mock_fetch
        yield mock_instance


@pytest.mark.asyncio
async def test_crawler_engine_basic(mock_client):
    engine = CrawlerEngine(start_url="https://example.com", max_pages=10)
    report = await engine.run()
    
    # Expected visited URLs:
    # 1. https://example.com (crawled, valid)
    # 2. https://example.com/page1 (crawled, valid)
    # 3. https://example.com/page2 (failed)
    # External link should be ignored.
    
    assert report.stats.pages_crawled == 2
    assert report.stats.pages_failed == 1
    assert report.stats.duration_seconds > 0
    assert engine.tracker.is_visited("https://example.com")
    assert engine.tracker.is_visited("https://example.com/page1")
    assert engine.tracker.is_visited("https://example.com/page2")
    assert not engine.tracker.is_visited("https://external.com")


@pytest.mark.asyncio
async def test_crawler_engine_max_pages(mock_client):
    engine = CrawlerEngine(start_url="https://example.com", max_pages=2)
    report = await engine.run()
    
    # Should stop after processing exactly 2 pages
    total_processed = report.stats.pages_crawled + report.stats.pages_failed
    assert total_processed == 2


@pytest.mark.asyncio
async def test_crawler_engine_redirect(mock_client):
    engine = CrawlerEngine(start_url="https://example.com/redirect", max_pages=10)
    report = await engine.run()
    
    # 1. /redirect (failed, because it's a 301, which has result.error_type if not 2xx. Wait, 301 has status_code=301 < 400. So it counts as crawled)
    # 2. /page1 (crawled)
    # 3. /page2 (failed)
    
    # Let's verify how 301 is handled. In client, < 500 returns early, so error_type is None.
    # In engine, status_code < 400 means crawled.
    # So /redirect is crawled, /page1 is crawled, /page2 is failed.
    assert report.stats.pages_crawled == 2
    assert report.stats.pages_failed == 1
    assert engine.tracker.is_visited("https://example.com/redirect")
    assert engine.tracker.is_visited("https://example.com/page1")
    assert engine.tracker.is_visited("https://example.com/page2")


@pytest.mark.asyncio
async def test_crawler_engine_max_depth(mock_client):
    engine = CrawlerEngine(start_url="https://example.com", max_pages=10, max_depth=0)
    report = await engine.run()
    
    # With max_depth=0, it should only crawl the start URL and not queue any extracted links
    assert report.stats.pages_crawled == 1
    assert report.stats.pages_failed == 0
    assert engine.tracker.is_visited("https://example.com")
    assert not engine.tracker.is_visited("https://example.com/page1")
