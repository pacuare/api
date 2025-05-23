from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.v1 import app as apiv1
from shared import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db.lifespan():
        yield

app = FastAPI(lifespan=lifespan)

app.mount('/v1', apiv1)
