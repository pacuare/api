import httpx
from clerk_backend_api import AuthenticateRequestOptions, Clerk

from shared.settings import Settings


def clerk(settings: Settings):
    return Clerk(settings.clerk_secret_key)

def authenticate_request(request: httpx.Request, settings: Settings):
    sdk = clerk(settings)
    return sdk.authenticate_request(
        request,
        AuthenticateRequestOptions(
        )
    )
