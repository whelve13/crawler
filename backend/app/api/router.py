from fastapi import APIRouter

from app.api.endpoints import crawl

api_router = APIRouter()
api_router.include_router(crawl.router, prefix="/crawl", tags=["crawl"])
