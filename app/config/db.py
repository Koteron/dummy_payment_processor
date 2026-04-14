from collections.abc import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from alembic.autogenerate import compare_metadata
from alembic.migration import MigrationContext

from app.models.base import Base
from app.config.settings import settings


engine = create_async_engine(settings.DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def verify_schema():
    async with engine.begin() as conn:
        def _sync_verify(sync_conn):
            ctx = MigrationContext.configure(sync_conn)
            diff = compare_metadata(ctx, Base.metadata)
            if diff:
                for d in diff:
                    print(d)
                raise RuntimeError("DB schema verification failed")
        
        await conn.run_sync(_sync_verify)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
