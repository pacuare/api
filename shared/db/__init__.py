from contextlib import asynccontextmanager
from typing import Any
from psycopg.abc import Params, Query
from psycopg_pool import AsyncConnectionPool
from os import environ

from shared import settings

pool = AsyncConnectionPool(settings.get().database_url, open=False)

@asynccontextmanager
async def lifespan():
    await pool.open()
    yield
    await pool.close()

async def query_one[T](sql: Query, params: Params = ()) -> T:
    async with pool.connection() as conn:
        res = (await (await conn.execute(sql, params)).fetchone())
        assert res is not None
        return res[0]
