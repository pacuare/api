from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException

from api.v1.auth import utils
from api.v1.auth.utils import require_user
from shared import db
from shared import settings
from shared.settings import Settings


router = APIRouter()

@router.get('/exists')
async def user_db_exists(email: Annotated[str, Depends(require_user)]):
    db_name = utils.get_user_database(email)
    return await db.query_one('select count(*)>0 from pg_catalog.pg_database where datname = %s', (db_name,))

@router.post('/create',
             responses={
                 200: {'description': 'Successfully created and initialized user database.'},
                 409: {'description': 'User database already exists; not created.'}
             })
async def create_user_db(email: Annotated[str, Depends(require_user)], settings: Annotated[Settings, Depends(settings.get)]):
    db_name = utils.get_user_database(email)

    if await user_db_exists(email):
        raise HTTPException(409, 'Database already exists')

    async with db.pool.connection() as conn:
        await conn.set_autocommit(True)
        await conn.execute('create database {}'.format(db_name))
        await conn.execute('select InitUserDatabase(%s, %s, %s)', (settings.database_url_base, settings.database_data, email))
    
    return db_name
