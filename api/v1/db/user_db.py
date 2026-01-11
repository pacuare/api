from contextlib import asynccontextmanager

import psycopg

from api.v1.auth import utils
from shared import settings


@asynccontextmanager
async def open_db(db: str):
    async with await psycopg.AsyncConnection.connect(
        settings.get().database_url_base + "/" + db
    ) as conn:
        yield conn


@asynccontextmanager
async def open_for(email: str):
    async with open_db(utils.get_user_database(email)) as conn:
        yield conn
