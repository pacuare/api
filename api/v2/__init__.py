from fastapi import FastAPI
from scalar_fastapi import get_scalar_api_reference

app = FastAPI(
    title="Pacuare Reserve",
    summary="Query the Pacuare Reserve dataset.",
    version="v2"
)

@app.get("/scalar", include_in_schema=False)
async def scalar_html():
    return get_scalar_api_reference(
        openapi_url='/v2/openapi.json',
        servers=[
            {
                'url': '/v2'
            }
        ],
        title=app.title
    )
