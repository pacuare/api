from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from api.v1 import app as apiv1
from api.v1.auth import AuthAccess, access_level, list_keys
from api.v1.auth.utils import get_user, require_user
from api.v1.db import user_db_exists
from api.v2 import app as apiv2
from shared import db, templates


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
    if 'Origin' in request.headers and request.headers['Origin'].endswith('.pacuare.dev') and response.headers['Access-Control-Allow-Origin'] == '*':
        response.headers['Access-Control-Allow-Origin'] = request.headers['Origin']
    return response

app.mount('/v1', apiv1)
app.mount('/v2', apiv2)

@app.get('/')
async def index(request: Request, user: Annotated[str|None, Depends(get_user)] = None):
    return templates.TemplateResponse(request, 'index.html', {
        'user': user,
        'full_access': (await access_level(user)).access_level == 'full' if user else None,
        'versions': ['v2', 'v1']
    })

@app.get('/login')
def login_page(request: Request, user: Annotated[str|None, Depends(get_user)] = None, return_to: Annotated[str, Query(alias="return")] = "/", error: bool = False):
    if user is not None:
        return RedirectResponse(return_to)
    return templates.TemplateResponse(request, 'login.html', {'return_to': return_to, 'error': error})

@app.get('/account')
def account_page(
    request: Request,
    user: Annotated[str, Depends(require_user)],
    db_exists: Annotated[bool, Depends(user_db_exists)],
    access: Annotated[AuthAccess, Depends(access_level)],
    api_keys: Annotated[list[tuple[int, str, str]], Depends(list_keys)]
):
    return templates.TemplateResponse(request, 'account.html',
        {
            'user': user,
            'has_db': db_exists,
            'full_access': access.access_level == 'full',
            'api_keys': [{'id': key[0], 'description': key[1], 'createdOn': key[2]} for key in api_keys]
        }
    )

@app.get('/health')
def health():
    return 'ok'

app.mount('/', StaticFiles(directory='static'))
