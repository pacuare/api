from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException

from api.v1.auth import utils
from api.v1.auth.utils import require_user
from api.v1.db import user_db
from shared import db, settings
from shared.settings import Settings

router = APIRouter()


@router.get("/exists")
async def user_db_exists(email: Annotated[str, Depends(require_user)]):
    db_name = utils.get_user_database(email)
    return await db.query_one(
        "select count(*)>0 from pg_catalog.pg_database where datname = %s", (db_name,)
    )


@router.post(
    "/create",
    responses={
        200: {"description": "Successfully created and initialized user database."},
        409: {"description": "User database already exists; not created."},
    },
)
async def create_user_db(
    email: Annotated[str, Depends(require_user)],
    settings: Annotated[Settings, Depends(settings.get)],
    refresh: Literal["none", "refresh", "recreate"] = "none",
):
    db_name = utils.get_user_database(email)
    db_exists = await user_db_exists(email)
    if db_exists and refresh == "none":
        raise HTTPException(409, "Database already exists")

    if db_exists and refresh == "refresh":
        async with user_db.open_for(email) as conn:
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
