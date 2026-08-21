import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base_class import Base

if TYPE_CHECKING:
    from app.models.issue import SEOIssue
    from app.models.task import CrawlTask


class Page(Base):
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    task_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("crawl_task.id", ondelete="CASCADE"), index=True)
    
    url: Mapped[str] = mapped_column(String, index=True)
    status_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    
    # Metadata
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    meta_description: Mapped[str | None] = mapped_column(String, nullable=True)
    canonical_url: Mapped[str | None] = mapped_column(String, nullable=True)
    language: Mapped[str | None] = mapped_column(String, nullable=True)
    robots_meta: Mapped[str | None] = mapped_column(String, nullable=True)
    
    # Structural (Store as arrays)
    h1_tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    h2_tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    h3_tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    internal_links: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    task: Mapped["CrawlTask"] = relationship("CrawlTask", back_populates="pages")
    seo_issues: Mapped[list["SEOIssue"]] = relationship("SEOIssue", back_populates="page", cascade="all, delete-orphan")
