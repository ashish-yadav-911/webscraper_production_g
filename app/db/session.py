from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

# In a real production app, you would use PostgreSQL
# DATABASE_URL = "postgresql+asyncpg://user:password@host/dbname"
DATABASE_URL = "sqlite+aiosqlite:///./scraper.db"

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)

Base = declarative_base()