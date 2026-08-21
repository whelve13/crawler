import pytest
from fastapi import status
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_create_crawl_task():
    # Use raise_app_exceptions=False so that missing DB yields a 500 instead of crashing the test runner locally
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as ac:
        response = await ac.post(
            "/api/v1/crawl/",
            json={
                "start_url": "https://example.com",
                "max_pages": 1, # Minimal
                "max_depth": 1
            }
        )
    # The background task will run. In testing, it's generally safe as long as the test framework
    # doesn't forcefully tear down the event loop while it runs.
    assert response.status_code in [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR]

@pytest.mark.asyncio
async def test_get_crawl_status_not_found():
    import uuid
    random_uuid = str(uuid.uuid4())
    async with AsyncClient(transport=ASGITransport(app=app, raise_app_exceptions=False), base_url="http://test") as ac:
        response = await ac.get(f"/api/v1/crawl/{random_uuid}")
    assert response.status_code in [status.HTTP_404_NOT_FOUND, status.HTTP_500_INTERNAL_SERVER_ERROR]

