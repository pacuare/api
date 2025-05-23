import psycopg

from api.v1 import auth
from shared import settings


async def open(email: str) -> psycopg.Connection:
    return psycopg.connect(settings.get().database_url_base + '/' + auth.get_user_database(email))