from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

from . import notebooks

app = FastAPI(
    title="Pacuare Reserve",
    summary="Query the Pacuare Reserve dataset and manage your account.",
    version="v1",
)

app.include_router(notebooks.router, prefix="/notebooks")


@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url="/v2/openapi.json", servers=[{"url": "/v2"}], title=app.title
    )
