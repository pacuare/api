from contextlib import asynccontextmanager
from typing import Literal

import psycopg
from fastapi import HTTPException

from shared import settings

from .. import db


def get_user_database(email: str) -> str:
    return "user_" + email.replace("@", "__").replace(".", "_")


@asynccontextmanager
async def open(email: str):
    async with await psycopg.AsyncConnection.connect(
        settings.get().database_url_base + "/" + get_user_database(email)
    ) as conn:
        yield conn


async def user_db_exists(email: str):
    db_name = get_user_database(email)
    return await db.query_one(
        "select count(*)>0 from pg_catalog.pg_database where datname = %s", (db_name,)
    )


async def create_user_db(
    email: str,
    settings: settings.Settings,
    refresh: Literal["none", "refresh", "recreate"] = "none",
):
    db_name = get_user_database(email)
    db_exists = await user_db_exists(email)
    if db_exists and refresh == "none":
        raise HTTPException(409, "Database already exists")

    if db_exists and refresh == "refresh":
        async with open(email) as conn:
            await conn.execute("drop table pacuare_raw")

    async with db.pool.connection() as conn:
        await conn.set_autocommit(True)
        if db_exists and refresh == "recreate":
            await conn.execute("drop database {}".format(db_name))  # ty:ignore[invalid-argument-type]
        if not (db_exists and refresh == "refresh"):
            await conn.execute("create database {}".format(db_name))  # ty:ignore[invalid-argument-type]
        await conn.execute(
            "select InitUserDatabase(%s, %s, %s)",
            (settings.database_url_base, settings.database_data, email),
        )

    return db_name
