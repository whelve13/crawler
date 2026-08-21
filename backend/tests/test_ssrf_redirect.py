from unittest.mock import AsyncMock, patch

import pytest

from app.crawler.engine import CrawlerEngine


@pytest.mark.asyncio
async def test_redirect_ssrf_protection():
    """
    Test that a public URL which redirects to a private IP is blocked
    and the private IP is not added to the fetch queue.
    """
    engine = CrawlerEngine("https://example.com", max_pages=3)
    
    # Mock client fetch to return a redirect to localhost on the first request
    async def mock_fetch(url, *args, **kwargs):
        from app.crawler.client import FetchResult
        if url == "https://example.com":
            return FetchResult(
                url=url, 
                status_code=302, 
                redirect_url="http://127.0.0.1:8000/admin"
            )
        return FetchResult(url=url, status_code=200)

    with patch.object(engine.client, 'fetch', new_callable=AsyncMock) as mock:
        mock.side_effect = mock_fetch
        
        await engine.run()
        
        # Ensure only the public URL was fetched
        mock.assert_called_once_with("https://example.com")
        
        # The crawler should not have visited the localhost URL
        assert not engine.tracker.is_visited("http://127.0.0.1:8000/admin")
