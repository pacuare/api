from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.params import Form
from fastapi.responses import RedirectResponse

from shared import db, enc, mailer, settings


router = APIRouter()

@router.get('/verify')
async def generate_code(email: str):
    has_user: bool = await db.query_one('select (count(*) > 0) from AuthorizedUsers where email=%s', email)

    if not has_user:
        return RedirectResponse('/')

    await mailer.send_confirmation(email)

    return 'sent'

@router.post('/verify',
             responses={
                200: {'description': 'Successfully verified and set cookie'},
                401: {'description': 'Verification failed'}
             })
async def verify(email: str, code: Annotated[str, Form], response: Response, settings: Annotated[settings.Settings, Depends(settings.get)]):
    expected_code: str = db.query_one('select code from LoginCodes where email=%s', (email,))
    if expected_code.lower() == code.lower():
        response.set_cookie('AuthStatus', enc.f.encrypt(email), domain=settings.cookie_domain, max_age=259200, path='/', secure=True, httponly=True)
        return 'ok'
    else:
        raise HTTPException(status_code=401, detail='Verification failed')

@router.post('/logout')
async def logout(response: Response, settings: Annotated[settings.Settings, Depends(settings.get)]):
    response.delete_cookie('AuthStatus', domain=settings.cookie_domain, path='/', secure=True, httponly=True)

def get_user(encrypted_cookie: str) -> str:
    
    return enc.f.decrypt(encrypted_cookie)

def get_user_database(email: str) -> str:
    return 'user_' + email.replace('@', '__').replace('.', '_')