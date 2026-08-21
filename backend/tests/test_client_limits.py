from unittest.mock import AsyncMock, patch

import pytest

from app.crawler.client import AsyncCrawlerClient


@pytest.mark.asyncio
async def test_oversized_response_terminated():
    client = AsyncCrawlerClient()
    
    # Mock httpx response stream
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/html", "Content-Length": str(10 * 1024 * 1024)} # 10MB
    
    # We need to mock the context manager returned by stream()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    
    with patch.object(client.client, 'stream', return_value=mock_context):
        result = await client.fetch("http://example.com")
        
    assert result.status_code == 413
    assert result.error_type == "ResponseTooLarge"
    assert result.html_content is None

@pytest.mark.asyncio
async def test_irrelevant_binary_skipped():
    client = AsyncCrawlerClient()
    
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/pdf"} 
    
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_response
    
    with patch.object(client.client, 'stream', return_value=mock_context):
        result = await client.fetch("http://example.com/file.pdf")
        
    assert result.status_code == 200
    # ensure it was not read
    mock_response.aiter_bytes.assert_not_called()
    assert result.html_content is None
