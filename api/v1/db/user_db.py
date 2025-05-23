from contextlib import asynccontextmanager
import psycopg

from api.v1.auth import utils
from shared import settings

@asynccontextmanager
async def open(email: str) :
    async with await psycopg.AsyncConnection.connect(settings.get().database_url_base + '/' + utils.get_user_database(email)) as conn:
        yield conn