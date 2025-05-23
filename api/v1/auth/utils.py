from encodings.hex_codec import hex_decode
from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2AuthorizationCodeBearer

from shared import db, enc

security_scheme = HTTPBearer(auto_error=False)

async def get_user(
        auth_status: Annotated[str|None, Cookie()] = None,
        api_key: Annotated[HTTPAuthorizationCredentials|None, Depends(security_scheme)] = None
        ) -> str | None:
    
    if auth_status is not None:
        return str(enc.f.decrypt(bytes.fromhex(auth_status)), 'utf-8')
    if api_key is not None:
        return await db.query_one[str]('select email from APIKeys where key = %s', api_key.credentials)

    return None

async def require_user(email: Annotated[str|None, Depends(get_user)]) -> str:
    if email is None:
        raise HTTPException(403, "Forbidden")
    return email

def get_user_database(email: str) -> str:
    return 'user_' + email.replace('@', '__').replace('.', '_')