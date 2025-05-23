from typing import Annotated, Any
from fastapi import APIRouter, Cookie, Depends, HTTPException
from psycopg import Connection
from pydantic import BaseModel

from api.v1.auth.utils import get_user, require_user
from api.v1.query import user_db
from shared import db


router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    params: tuple[str] | None = None

class QueryResponse(BaseModel):
    columns: tuple[str]
    values: list[tuple[Any]]

@router.post('')
async def query(email: Annotated[str, Depends(require_user)], req: QueryRequest) -> QueryResponse:
    full_access = db.query_one[bool]('select fullAccess from AuthorizedUsers where email=%s', (email,))
    
    async with (db.pool.connection() if full_access else user_db.open(email)) as conn:
        res = await conn.execute(req.query, req.params)
        return QueryResponse(
            columns=[c.name for c in res.description],
            values=await res.fetchall()
        )