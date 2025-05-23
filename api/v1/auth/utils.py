from encodings.hex_codec import hex_decode
from typing import Annotated

from fastapi import Cookie, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2AuthorizationCodeBearer

from shared import db, enc

security_scheme = HTTPBearer()

async def get_user(
        auth_status: Annotated[str|None, Cookie()] = None,
        api_key: Annotated[HTTPAuthorizationCredentials|None, Depends(security_scheme)] = None
        ) -> str | None:
    
    if auth_status is not None:
        return enc.f.decrypt(hex_decode(auth_status)[0])
    if api_key is not None:
        return await db.query_one[str]('select email from APIKeys where key = %s', api_key.credentials)

    return None

async def require_user(email: Annotated[str|None, Depends(get_user)]) -> str:
    assert email is not None
    return email

def get_user_database(email: str) -> str:
    return 'user_' + email.replace('@', '__').replace('.', '_')