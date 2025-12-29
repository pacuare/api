from encodings.hex_codec import hex_encode
from typing import Annotated, Literal

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, Request, Response
from fastapi.params import Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel

from api.v1.auth.utils import require_user
from shared import db, enc, mailer, settings

router = APIRouter()

@router.get('/verify')
async def generate_code(email: str):
    has_user: bool = await db.query_one('select (count(*) > 0) from AuthorizedUsers where email=%s', (email,))

    if not has_user:
        raise HTTPException(403, 'Forbidden')

    await mailer.send_confirmation(email)

    return 'sent'

@router.post('/verify',
             responses={
                200: {'description': 'Successfully verified and set cookie'},
                401: {'description': 'Verification failed'}
             })
async def verify(email: Annotated[str, Form()], code: Annotated[str, Form()], response: Response, settings: Annotated[settings.Settings, Depends(settings.get)], return_to: Annotated[str|None, Form()]):
    expected_code: str = await db.query_one('select code from LoginCodes where email=%s', (email,))
    if return_to is not None:
        resp = RedirectResponse(return_to, 303)
    else:
        resp = response
    if expected_code.lower() == code.lower():
        async with db.pool.connection() as conn:
            await conn.execute('delete from LoginCodes where email=%s', (email,))
        resp.set_cookie('auth_status', enc.f.encrypt(bytes(email, 'utf-8')).hex(), domain=settings.cookie_domain, max_age=259200, path='/', secure=True, httponly=True, samesite='none')
        return resp
    else:
        if return_to is not None:
            return RedirectResponse('/login?error=true', 303)
        else:
            raise HTTPException(status_code=401, detail='Verification failed')

class AuthAccess(BaseModel):
    email: str
    access_level: Literal['full', 'restricted']

@router.get('/access')
async def access_level(email: Annotated[str, Depends(require_user)]) -> AuthAccess:
    full_access: bool = await db.query_one('select fullAccess from AuthorizedUsers where email=%s', (email,))
    return AuthAccess(
        email= email,
        access_level= 'full' if full_access else 'restricted'
    )

@router.get('/logout')
@router.post('/logout')
async def logout(req: Request, response: Response, settings: Annotated[settings.Settings, Depends(settings.get)], return_to: Annotated[str, Query(alias='return')] = '/'):
    resp = response
    if req.method.lower() == 'get':
        resp = RedirectResponse(return_to)
    resp.delete_cookie('auth_status', domain=settings.cookie_domain, path='/', secure=True, httponly=True)
    return resp

@router.get('/key')
async def generate_key(description: str, email: Annotated[str, Depends(require_user)]):
    (key, id, desc, created_on) = await db.query_one('insert into APIKeys (email, description) values (%s, %s) returning (key, id, description, to_char(createdOn, \'YYYY-MM-DD\'))', (email, description))
    return {'key': key, 'id': id, 'description': desc, 'createdOn': created_on}

@router.delete('/key')
async def delete_key(id: int, email: Annotated[str, Depends(require_user)]) -> int:
    async with db.pool.connection() as conn:
        await conn.execute('delete from APIKeys where id = %s and email = %s', (id, email))
    return id

@router.get('/keys')
async def list_keys(email: Annotated[str, Depends(require_user)]) -> list[tuple[int, str, str]]:
    async with db.pool.connection() as conn:
        return await (await conn.execute("""
            select id, description, to_char("createdOn", 'YYYY-MM-DD') as "createdOn"
                from APIKeys
                where email = %s
                order by "createdOn" asc
        """, (email,))).fetchall()
