from app.db.base_class import Base
from app.models.issue import HealthIssue, SEOIssue
from app.models.page import Page
from app.models.task import CrawlTask

__all__ = ["Base", "CrawlTask", "HealthIssue", "Page", "SEOIssue"]
