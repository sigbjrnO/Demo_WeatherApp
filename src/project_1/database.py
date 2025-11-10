from sqlalchemy.ext.asyncio import create_async_engine

import database_tables

async def start_engine(app):
    engine = create_async_engine("sqlite+aiosqlite:///database.db", echo=False)

    async with engine.begin() as conn:
        await conn.run_sync(database_tables.meta.create_all)

    app["db_engine"] = engine

async def stop_engine(app):
    await app["db_engine"].dispose()