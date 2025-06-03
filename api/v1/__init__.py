from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from . import auth, query, db

app = FastAPI(
    title="Pacuare Reserve",
    summary="Query the Pacuare Reserve dataset.",
    version="v1"
)

app.include_router(auth.router, prefix='/auth')
app.include_router(query.router, prefix='/query')
app.include_router(db.router, prefix='/db')

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url='/v1/openapi.json',
        servers=[
            {
                'url': '/v1'
            }
        ],
        title=app.title
    )
