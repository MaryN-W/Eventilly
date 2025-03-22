from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.config import Config

# Async engine
engine = create_async_engine(
    Config.DATABASE_URL,  # Ensure this uses postgresql+asyncpg://
    echo=True,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# Async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession, 
    expire_on_commit=False
)

# Async session dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session