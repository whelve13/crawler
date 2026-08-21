import uuid

from pydantic import BaseModel


class CrawlRequest(BaseModel):
    start_url: str
    max_pages: int = 50
    max_depth: int = 3
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
