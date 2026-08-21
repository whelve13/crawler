from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.crawler.client import AsyncCrawlerClient


@pytest.fixture
async def crawler_client():
    client = AsyncCrawlerClient(max_connections=2, timeout=1.0)
    yield client
    await client.close()

@pytest.mark.asyncio
async def test_successful_fetch(crawler_client):
    # Mock transport
    def handler(request: httpx.Request):
        return httpx.Response(
            200, 
            headers={"Content-Type": "text/html; charset=utf-8"}, 
            text="<html>Hello</html>"
        )
    
    crawler_client.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    
    result = await crawler_client.fetch("https://example.com")
    
    assert result.status_code == 200
    assert result.html_content == "<html>Hello</html>"
    assert result.error_type is None
    assert result.redirect_url is None
    assert result.response_time >= 0.0

@pytest.mark.asyncio
async def test_redirect_handling(crawler_client):
    def handler(request: httpx.Request):
        return httpx.Response(
            301,
            headers={"Location": "https://example.com/new"}
        )
    
    crawler_client.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    
    result = await crawler_client.fetch("https://example.com")
    
    assert result.status_code == 301
    assert result.redirect_url == "https://example.com/new"
    assert result.html_content is None

@pytest.mark.asyncio
async def test_timeout_retry(crawler_client):
    # Track calls to ensure retry logic is working
    call_count = 0
    
    def handler(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        raise httpx.ReadTimeout("Timeout")
    
    crawler_client.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    
    # We patch asyncio.sleep so we don't actually wait during tests
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await crawler_client.fetch("https://example.com", max_retries=2)
        
        assert call_count == 3  # Initial + 2 retries
        assert result.error_type == "Timeout"
        assert result.status_code is None
        assert mock_sleep.call_count == 2

@pytest.mark.asyncio
async def test_server_error_retry(crawler_client):
    call_count = 0
    
    def handler(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(500, text="Internal Server Error")
    
    crawler_client.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await crawler_client.fetch("https://example.com", max_retries=1)
        
        assert call_count == 2
        assert result.status_code == 500
        assert result.error_type == "HTTP_500"
        assert mock_sleep.call_count == 1

@pytest.mark.asyncio
async def test_client_error_no_retry(crawler_client):
    call_count = 0
    
    def handler(request: httpx.Request):
        nonlocal call_count
        call_count += 1
        return httpx.Response(404, text="Not Found")
    
    crawler_client.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
    
    with patch("asyncio.sleep", new_callable=AsyncMock) as mock_sleep:
        result = await crawler_client.fetch("https://example.com", max_retries=2)
        
        assert call_count == 1  # Should not retry on 404
        assert result.status_code == 404
        assert result.error_type is None
        assert mock_sleep.call_count == 0
