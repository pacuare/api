import io
from typing import Annotated, Any, Iterable, Sequence, cast
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response
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

async def query_base(email: str, req: QueryRequest) -> QueryResponse: 
    full_access: bool = await db.query_one('select fullAccess from AuthorizedUsers where email=%s', (email,))
    
    async with (db.pool.connection() if full_access else user_db.open(email)) as conn:
        res = await conn.execute(cast(Query, req.query), tuple(req.params if req.params is not None else []))

        return QueryResponse(
            columns=[c.name for c in res.description] if res.description != None else [],
            values=cast(list[list[Any]], await res.fetchall()) if res.description is not None else []
        )

# Adapted from https://stackoverflow.com/a/74015930
async def extract_query(req: Request) -> QueryRequest:
    content_type = req.headers.get('Content-Type')
    if content_type is None:
        content_type = 'application/json'
    if content_type == 'application/json':
        return QueryRequest.model_validate(await req.json())
    elif (content_type == 'application/x-www-form-urlencoded' or
          content_type.startswith('multipart/form-data')):
        return QueryRequest.model_validate(await req.form())
    else:
        raise HTTPException(400, 'Invalid Content-Type')

@router.post('')
async def query(email: Annotated[str, Depends(require_user)], req: Annotated[QueryRequest, Depends(extract_query)], hreq: Request, resp: Response) -> QueryResponse:
    resp.headers['Access-Control-Allow-Origin'] = hreq.headers['Origin'] if 'Origin' in hreq.headers else '*'
    return await query_base(email, req)

@router.post('.csv')
async def query_csv(email: Annotated[str, Depends(require_user)], req: Annotated[QueryRequest, Depends(extract_query)], hreq: Request) -> StreamingResponse:
    """Query the database, returning the response as a CSV table instead of JSON."""
    qres = await query_base(email, req)

    df = pd.DataFrame.from_records(qres.values, columns=qres.columns)
    stream = io.StringIO()
    df.to_csv(stream, index=False)

    resp = StreamingResponse(iter([stream.getvalue()]), media_type='text/csv')

    resp.headers['Access-Control-Allow-Origin'] = hreq.headers['Origin'] if 'Origin' in hreq.headers else '*'
    resp.headers['Content-Disposition'] = 'attachment;filename=query.csv'

    return resp
