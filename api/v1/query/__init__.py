from typing import Annotated, Any
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from api.v1.auth.utils import require_user
from api.v1.db import user_db
from shared import db


router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    params: list[str] | None = None

class QueryResponse(BaseModel):
    columns: list[str]
    values: list[list[Any]]

@router.post('')
async def query(email: Annotated[str, Depends(require_user)], req: QueryRequest) -> QueryResponse:
    full_access: bool = await db.query_one('select fullAccess from AuthorizedUsers where email=%s', (email,))
    
    async with (db.pool.connection() if full_access else user_db.open(email)) as conn:
        res = await conn.execute(req.query, tuple(req.params))

        return QueryResponse(
            columns=[c.name for c in res.description] if res.description != None else [],
            values=(await res.fetchall()) if res.description != None else []
        )