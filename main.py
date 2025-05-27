from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from api.v1 import app as apiv1
from shared import db
from fastapi.middleware.cors import CORSMiddleware

templates = Jinja2Templates(directory='templates')

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with db.lifespan():
        yield

app = FastAPI(
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware('http')
async def subdomain_cors(request: Request, call_next):
    response: Response = await call_next(request)
    if request.headers['Origin'].endswith('.pacuare.dev') and response.headers['Access-Control-Allow-Origin'] == '*':
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    return response

app.mount('/v1', apiv1)

@app.get('/')
def index(request: Request):
    return templates.TemplateResponse(request, 'index.html', {
        'versions': ['v1']
    })

@app.get('/health')
def health():
    return 'ok'