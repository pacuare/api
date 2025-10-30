import io
from typing import Annotated, Any, Iterable, cast
from api.v1.auth import utils
from fastapi import APIRouter, Depends, Form, Request, Response
from fastapi.responses import StreamingResponse
from psycopg.abc import Query
from pydantic import BaseModel
import pandas as pd

from api.v1.auth.utils import require_user
from api.v1.db import user_db
from shared import db
from shared import settings
from shared.settings import Settings


router = APIRouter()


class QueryRequest(BaseModel):
    query: str
    params: Iterable[str] | None = None


class QueryResponse(BaseModel):
    columns: list[str]
    values: list[list[Any]]


def set_query_headers(hreq: Request, resp: Response):
    resp.headers["access-control-allow-origin"] = (
        hreq.headers["origin"] if "origin" in hreq.headers else "*"
    )


async def query_base(
    email: str,
    req: QueryRequest,
    settings: Settings,
    hreq: Request,
    resp: Response | None,
) -> QueryResponse:
    if resp is not None:
        set_query_headers(hreq, resp)
    full_access: bool = await db.query_one(
        "select fullAccess from AuthorizedUsers where email=%s", (email,)
    )

    print(
        "Querying on database "
        + (settings.database_data if full_access else utils.get_user_database(email))
    )

    async with db.pool.connection() if full_access else user_db.open(email) as conn:
        res = await conn.execute(cast(Query, req.query), tuple(req.params or []))

        return QueryResponse(
            columns=[c.name for c in res.description]
            if res.description is not None
            else [],
            values=cast(list[list[str]], await res.fetchall())
            if res.description is not None
            else [],
        )


@router.post("")
async def query(
    email: Annotated[str, Depends(require_user)],
    settings: Annotated[Settings, Depends(settings.get)],
    req: QueryRequest,
    hreq: Request,
    resp: Response,
) -> QueryResponse:
    return await query_base(email, req, settings, hreq, resp)


@router.post("/form")
async def query_form(
    email: Annotated[str, Depends(require_user)],
    settings: Annotated[Settings, Depends(settings.get)],
    req: Annotated[QueryRequest, Form()],
    hreq: Request,
    resp: Response,
) -> QueryResponse:
    return await query_base(email, req, settings, hreq, resp)


class CSVResponseClass(StreamingResponse):
    media_type = "text/csv"
    openapi_response = {
        "description": "A CSV containing the results of your query",
        "content": {
            "text/csv": {
                "schema": {
                    "type": "string",
                    "example": """header1,header2
value1,value2""",
                }
            }
        },
    }


@router.post(
    ".csv",
    response_class=CSVResponseClass,
    responses={200: CSVResponseClass.openapi_response},
)
async def query_csv(
    email: Annotated[str, Depends(require_user)],
    req: QueryRequest,
    settings: Annotated[Settings, Depends(settings.get)],
    hreq: Request,
    resp: CSVResponseClass,
):
    """Query the database, returning the response as a CSV table instead of JSON."""

    qres = await query_base(email, req, settings, hreq, None)
    stream = io.StringIO()

    df = pd.DataFrame.from_records(qres.values, columns=qres.columns)
    df.to_csv(stream, index=False)
    set_query_headers(hreq, resp)
    resp.headers["Content-Disposition"] = "attachment;filename=query.csv"

    return stream.getvalue()


@router.post(
    ".csv/form",
    response_class=CSVResponseClass,
    responses={200: CSVResponseClass.openapi_response},
)
async def query_form_csv(
    email: Annotated[str, Depends(require_user)],
    req: Annotated[QueryRequest, Form()],
    settings: Annotated[Settings, Depends(settings.get)],
    hreq: Request,
    resp: CSVResponseClass,
):
    return await query_csv(email, req, settings, hreq, resp)
