# This file is used to create all tables in the database.
# To run this file use >> python -m src.db.init_db
from src.db.base import Base
from src.database import engine
import asyncio
from sqlalchemy import text
async def init_db():
    async with engine.begin() as conn:
        await conn.execute(text("DROP TABLE IF EXISTS registrations CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS events CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS attendees CASCADE"))
        await conn.execute(text("DROP TABLE IF EXISTS categories CASCADE"))
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables recreated!")

if __name__ == "__main__":
    asyncio.run(init_db())