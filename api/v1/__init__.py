from fastapi import FastAPI

from . import auth
from . import query

app = FastAPI(
    title="Pacuare Reserve",
    summary="Query the Pacuare Reserve dataset.",
    version="v1"
)

app.include_router(auth.router, prefix='/auth')
app.include_router(query.router, prefix='/query')