from typing import Annotated

from fastapi import Cookie, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from shared import db, enc

security_scheme = HTTPBearer(auto_error=False)


async def get_user(
    auth_status: Annotated[str | None, Cookie()] = None,
    api_key: Annotated[
        HTTPAuthorizationCredentials | None, Depends(security_scheme)
    ] = None,
) -> str | None:
    if auth_status is not None:
        return str(enc.f.decrypt(bytes.fromhex(auth_status)), "utf-8")
    if api_key is not None:
        return await db.query_one(
            "select email from APIKeys where key = %s", (api_key.credentials,)
        )

    return None


GetUser = Annotated[str | None, Depends(get_user)]


async def require_user(email: GetUser) -> str:
    if email is None:
        raise HTTPException(403, "Forbidden")
    return email


RequireUser = Annotated[str, Depends(require_user)]


def get_user_database(email: RequireUser) -> str:
    return "user_" + email.replace("@", "__").replace(".", "_")


GetUserDatabase = Annotated[str, Depends(get_user_database)]
