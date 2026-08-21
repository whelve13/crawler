import logging
import uuid

from app.crawler.engine import CrawlerEngine
from app.db.session import AsyncSessionLocal
from app.models.issue import HealthIssue, SEOIssue
from app.models.page import Page
from app.models.task import CrawlTask

logger = logging.getLogger(__name__)

async def run_crawl_task(
    task_id: uuid.UUID,
    start_url: str,
    max_pages: int,
    max_depth: int,
    check_external_links: bool,
):
    """
    Background job to execute the crawl engine and persist the results.
    """
    # 1. Update status to running
    async with AsyncSessionLocal() as session:
        task = await session.get(CrawlTask, task_id)
        if not task:
            logger.error(f"Task {task_id} not found to start.")
            return
        task.status = "running"
        await session.commit()

    engine = CrawlerEngine(
        start_url=start_url,
        max_pages=max_pages,
        max_depth=max_depth,
        check_external_links=check_external_links,
    )

    try:
        # 2. Run crawler
        report = await engine.run()

        # 3. Persist results
        async with AsyncSessionLocal() as session:
            task = await session.get(CrawlTask, task_id)
            if not task:
                return

            task.status = "completed"
            task.pages_crawled = report.stats.pages_crawled
            task.pages_failed = report.stats.pages_failed
            task.duration_seconds = report.stats.duration_seconds

            for page_data in report.pages:
                db_page = Page(
                    task_id=task_id,
                    url=page_data.url,
                    status_code=page_data.status_code,
                    title=page_data.title,
                    meta_description=page_data.meta_description,
                    canonical_url=page_data.canonical_url,
                    language=page_data.language,
                    robots_meta=page_data.robots_meta,
                    h1_tags=page_data.h1_tags,
                    h2_tags=page_data.h2_tags,
                    h3_tags=page_data.h3_tags,
                    internal_links=page_data.internal_links,
                )
                session.add(db_page)
                await session.flush()  # to get db_page.id

                for issue in page_data.seo_issues:
                    db_issue = SEOIssue(
                        page_id=db_page.id,
                        rule_id=issue.rule_id,
                        severity=issue.severity,
                        message=issue.message,
                        element=issue.element,
                    )
                    session.add(db_issue)

            for h_issue in report.health_issues:
                db_h_issue = HealthIssue(
                    task_id=task_id,
                    url=h_issue.url,
                    issue_type=h_issue.issue_type,
                    description=h_issue.description,
                )
                session.add(db_h_issue)

            await session.commit()
            logger.info(f"Task {task_id} completed successfully.")

    except Exception:
        logger.exception(f"Task {task_id} failed with exception")
        async with AsyncSessionLocal() as session:
            task = await session.get(CrawlTask, task_id)
            if task:
                task.status = "failed"
                await session.commit()
