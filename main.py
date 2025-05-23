from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from api.v1 import app as apiv1
from shared import db

templates = Jinja2Templates(directory='templates')

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db.lifespan():
        yield

app = FastAPI(
    lifespan=lifespan,
)

app.mount('/v1', apiv1)

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(request, 'index.html', {
        'versions': ['v1']
    })
