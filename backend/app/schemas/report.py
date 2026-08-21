
from pydantic import BaseModel, Field


class SEOIssueSchema(BaseModel):
    rule_id: str
    severity: str
    message: str
    element: str | None = None


class PageReportSchema(BaseModel):
    url: str
    status_code: int | None = None
    title: str | None = None
    meta_description: str | None = None
    canonical_url: str | None = None
    language: str | None = None
    robots_meta: str | None = None
    h1_tags: list[str] = Field(default_factory=list)
    h2_tags: list[str] = Field(default_factory=list)
    h3_tags: list[str] = Field(default_factory=list)
    internal_links: list[str] = Field(default_factory=list)
    seo_issues: list[SEOIssueSchema] = Field(default_factory=list)


class HealthIssueSchema(BaseModel):
    url: str
    issue_type: str
    description: str


class CrawlStatsSchema(BaseModel):
    pages_crawled: int
    pages_failed: int
    duration_seconds: float


class CrawlReportSchema(BaseModel):
    start_url: str
    stats: CrawlStatsSchema
    pages: list[PageReportSchema] = Field(default_factory=list)
    health_issues: list[HealthIssueSchema] = Field(default_factory=list)
