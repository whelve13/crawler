import uuid

from pydantic import BaseModel, Field, HttpUrl


class CrawlRequest(BaseModel):
    start_url: HttpUrl
    max_pages: int = Field(default=50, ge=1, le=500)
    max_depth: int = Field(default=3, ge=1, le=5)
    check_external_links: bool = False

class CrawlResponse(BaseModel):
    task_id: uuid.UUID
    status: str
    
class CrawlTaskStatusResponse(BaseModel):
    task_id: uuid.UUID
    status: str
    pages_crawled: int
    pages_failed: int
    duration_seconds: float
