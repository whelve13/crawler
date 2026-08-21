from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.SQLALCHEMY_DATABASE_URI,
    echo=False,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW,
    pool_pre_ping=True
)
AsyncSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine)
