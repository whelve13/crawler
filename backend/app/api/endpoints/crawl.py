import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.concurrency import concurrency_manager
from app.core.rate_limit import limiter
from app.db.session import AsyncSessionLocal
from app.models.page import Page
from app.models.task import CrawlTask
from app.schemas.crawl import CrawlRequest, CrawlResponse, CrawlTaskStatusResponse
from app.schemas.report import (
    CrawlReportSchema,
    CrawlStatsSchema,
    HealthIssueSchema,
    PageReportSchema,
    SEOIssueSchema,
)
from app.services.crawler import run_crawl_task

router = APIRouter()

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@router.post("/", response_model=CrawlResponse)
@limiter.limit("5/minute")
async def start_crawl(
    request: Request,
    payload: CrawlRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    if not concurrency_manager.can_start():
        raise HTTPException(status_code=503, detail="Server is currently at maximum crawl capacity. Please try again later.")
    # Create task in DB
    task = CrawlTask(
        start_url=str(payload.start_url),
        status="pending"
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    
    # Enqueue background job
    background_tasks.add_task(
        run_crawl_task,
        task_id=task.id,
        start_url=str(payload.start_url),
        max_pages=payload.max_pages,
        max_depth=payload.max_depth,
        check_external_links=payload.check_external_links
    )
    
    return CrawlResponse(task_id=task.id, status=task.status)

@router.get("/", response_model=list[CrawlTaskStatusResponse])
@limiter.limit("30/minute")
async def get_recent_tasks(request: Request, limit: int = 10, db: AsyncSession = Depends(get_db)):
    stmt = select(CrawlTask).order_by(CrawlTask.created_at.desc()).limit(limit)
    result = await db.execute(stmt)
    tasks = result.scalars().all()
    return [
        CrawlTaskStatusResponse(
            task_id=task.id,
            status=task.status,
            pages_crawled=task.pages_crawled,
            pages_failed=task.pages_failed,
            duration_seconds=task.duration_seconds
        )
        for task in tasks
    ]

@router.get("/{task_id}", response_model=CrawlTaskStatusResponse)
@limiter.limit("60/minute")
async def get_crawl_status(request: Request, task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    task = await db.get(CrawlTask, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    return CrawlTaskStatusResponse(
        task_id=task.id,
        status=task.status,
        pages_crawled=task.pages_crawled,
        pages_failed=task.pages_failed,
        duration_seconds=task.duration_seconds
    )

@router.get("/{task_id}/report", response_model=CrawlReportSchema)
@limiter.limit("30/minute")
async def get_crawl_report(request: Request, task_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    # Eagerly load all relationships
    stmt = select(CrawlTask).where(CrawlTask.id == task_id).options(
        selectinload(CrawlTask.pages).selectinload(Page.seo_issues),
        selectinload(CrawlTask.health_issues)
    )
    
    result = await db.execute(stmt)
    task = result.scalar_one_or_none()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    if task.status != "completed":
        raise HTTPException(status_code=400, detail=f"Report not available. Task status is {task.status}")
        
    # Serialize back to CrawlReportSchema
    stats = CrawlStatsSchema(
        pages_crawled=task.pages_crawled,
        pages_failed=task.pages_failed,
        duration_seconds=task.duration_seconds
    )
    
    pages = []
    for p in task.pages:
        issues = [
            SEOIssueSchema(
                rule_id=i.rule_id,
                severity=i.severity,
                message=i.message,
                element=i.element
            )
            for i in p.seo_issues
        ]
        pages.append(PageReportSchema(
            url=p.url,
            status_code=p.status_code,
            title=p.title,
            meta_description=p.meta_description,
            canonical_url=p.canonical_url,
            language=p.language,
            robots_meta=p.robots_meta,
            h1_tags=p.h1_tags,
            h2_tags=p.h2_tags,
            h3_tags=p.h3_tags,
            internal_links=p.internal_links,
            seo_issues=issues
        ))
        
    health_issues = [
        HealthIssueSchema(
            url=h.url,
            issue_type=h.issue_type,
            description=h.description
        )
        for h in task.health_issues
    ]
    
    return CrawlReportSchema(
        start_url=task.start_url,
        stats=stats,
        pages=pages,
        health_issues=health_issues
    )
