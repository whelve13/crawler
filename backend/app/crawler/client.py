import asyncio
import time
from dataclasses import dataclass

import httpx

from app.core.config import settings


@dataclass
class FetchResult:
    url: str
    status_code: int | None = None
    html_content: str | None = None
    response_time: float = 0.0
    error_type: str | None = None
    redirect_url: str | None = None


class AsyncCrawlerClient:
    """
    A reusable, asynchronous HTTP client for the crawler.
    Features:
    - Connection pooling
    - Configurable timeouts
    - Configurable User-Agent
    - Retry handling
    - Redirect capture
    - Exception classification
    """

    def __init__(
        self,
        max_connections: int = settings.MAX_CONCURRENCY,
        timeout: float = settings.DEFAULT_TIMEOUT,
        user_agent: str = settings.USER_AGENT,
    ):
        limits = httpx.Limits(
            max_keepalive_connections=max_connections,
            max_connections=max_connections,
        )
        timeout_config = httpx.Timeout(timeout)
        headers = {"User-Agent": user_agent}

        self.client = httpx.AsyncClient(
            limits=limits,
            timeout=timeout_config,
            headers=headers,
            # We don't automatically follow redirects so the crawler can track chains, loops, and boundaries
            follow_redirects=False,
        )

    async def fetch(self, url: str, max_retries: int = 3) -> FetchResult:
        """
        Fetch a URL with retry logic, capturing status, timing, and errors.
        """
        retries = 0
        backoff = 1.0
        last_result = None

        while retries <= max_retries:
            start_time = time.monotonic()
            try:
                MAX_BYTES = settings.MAX_FILE_SIZE_BYTES  # Use limits from settings
                
                async with self.client.stream("GET", url) as response:
                    response_time = time.monotonic() - start_time
                    result = FetchResult(
                        url=url,
                        status_code=response.status_code,
                        response_time=response_time,
                    )
                    
                    # Handle Redirects
                    if response.status_code in (301, 302, 303, 307, 308):
                        result.redirect_url = response.headers.get("Location")
                        
                    # Parse body only for successful HTML responses to save memory
                    content_type = response.headers.get("Content-Type", "")
                    content_length = response.headers.get("Content-Length")
                    
                    if response.status_code == 200 and "text/html" in content_type.lower():
                        # If the server tells us it's too big upfront, skip downloading
                        if content_length and int(content_length) > MAX_BYTES:
                            result.error_type = "ResponseTooLarge"
                            result.status_code = 413 # Payload Too Large semantic mapped to client side
                        else:
                            content_chunks = []
                            total_bytes = 0
                            async for chunk in response.aiter_bytes():
                                content_chunks.append(chunk)
                                total_bytes += len(chunk)
                                if total_bytes > MAX_BYTES:
                                    break
                            result.html_content = b"".join(content_chunks).decode("utf-8", errors="ignore")
                        
                # Return on successful fetch or client errors (no retry for 4xx)
                if result.status_code < 500:
                    return result

                # 5xx errors fall through to retry
                result.error_type = f"HTTP_{result.status_code}"
                last_result = result
                
            except httpx.TimeoutException:
                response_time = time.monotonic() - start_time
                last_result = FetchResult(
                    url=url, response_time=response_time, error_type="Timeout"
                )
            except httpx.RequestError as e:
                response_time = time.monotonic() - start_time
                last_result = FetchResult(
                    url=url, response_time=response_time, error_type=f"RequestError: {type(e).__name__}"
                )
            except Exception as e:  # noqa: BLE001
                response_time = time.monotonic() - start_time
                last_result = FetchResult(
                    url=url, response_time=response_time, error_type=f"UnexpectedError: {type(e).__name__}"
                )

            retries += 1
            if retries <= max_retries:
                await asyncio.sleep(backoff)
                backoff *= 2  # Exponential backoff

        return last_result

    async def close(self):
        """Close the underlying HTTPX client."""
        await self.client.aclose()
