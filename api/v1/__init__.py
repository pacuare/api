from fastapi import FastAPI

from . import auth, query, db

app = FastAPI(
    title="Pacuare Reserve",
    summary="Query the Pacuare Reserve dataset.",
    version="v1"
)

app.include_router(auth.router, prefix='/auth')
app.include_router(query.router, prefix='/query')
app.include_router(db.router, prefix='/db')