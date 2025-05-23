from fastapi import FastAPI

from . import auth
from . import query

app = FastAPI()
app.include_router(auth.router, prefix='/auth')
app.include_router(query.router, prefix='/query')