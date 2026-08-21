import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.page import Page
    from app.models.task import CrawlTask



class SEOIssue(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    page_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("page.id", ondelete="CASCADE"), index=True)
    
    rule_id: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    message: Mapped[str] = mapped_column(String)
    element: Mapped[str | None] = mapped_column(String, nullable=True)

    page: Mapped["Page"] = relationship("Page", back_populates="seo_issues")


class HealthIssue(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("crawl_task.id", ondelete="CASCADE"), index=True)
    
    url: Mapped[str] = mapped_column(String, index=True)
    issue_type: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)

    task: Mapped["CrawlTask"] = relationship("CrawlTask", back_populates="health_issues")
