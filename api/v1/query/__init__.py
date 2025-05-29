import io
from typing import Annotated, Any, Iterable, cast
from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import StreamingResponse
from psycopg.abc import Query
from pydantic import BaseModel
import pandas as pd

from api.v1.auth.utils import require_user
from api.v1.db import user_db
from shared import db


router = APIRouter()

class QueryRequest(BaseModel):
    query: str
    params: Iterable[str] | None = None

class QueryResponse(BaseModel):
    columns: list[str]
    values: list[list[Any]]

def set_query_headers(hreq: Request, resp: Response):
    resp.headers['access-control-allow-origin'] = hreq.headers['origin'] if 'origin' in hreq.headers else '*'


async def query_base(email: str, req: QueryRequest, hreq: Request, resp: Response | None) -> QueryResponse: 
    if resp is not None:
        set_query_headers(hreq, resp)    
    full_access: bool = await db.query_one('select fullAccess from AuthorizedUsers where email=%s', (email,))
    
    async with (db.pool.connection() if full_access else user_db.open(email)) as conn:
        res = await conn.execute(cast(Query, req.query), tuple(req.params or []))

        return QueryResponse(
            columns=[c.name for c in res.description] if res.description != None else [],
            values=cast(list[list[str]], await res.fetchall()) if res.description != None else []
        )

@router.post('')
async def query(email: Annotated[str, Depends(require_user)], req: QueryRequest, hreq: Request, resp: Response) -> QueryResponse:
    return await query_base(email, req, hreq, resp)

@router.post('/form')
async def query_form(email: Annotated[str, Depends(require_user)], req: Annotated[QueryRequest, Form()], hreq: Request, resp: Response) -> QueryResponse:
    return await query_base(email, req, hreq, resp)

@router.post('.csv')
async def query_csv(email: Annotated[str, Depends(require_user)], req: QueryRequest, hreq: Request) -> StreamingResponse:
    """Query the database, returning the response as a CSV table instead of JSON."""
    
    qres = await query_base(email, req, hreq, None)
    stream = io.StringIO()
    
    df = pd.DataFrame.from_records(qres.values, columns=qres.columns)
    df.to_csv(stream, index=False)
    resp = StreamingResponse(iter([stream.getvalue()]), media_type='text/csv')
    set_query_headers(hreq, resp)
    resp.headers['Content-Disposition'] = 'attachment;filename=query.csv'

    return resp

@router.post('.csv/form')
async def query_form_csv(email: Annotated[str, Depends(require_user)], req: Annotated[QueryRequest, Form()], hreq: Request) -> StreamingResponse:
    return await query_csv(email, req, hreq)
