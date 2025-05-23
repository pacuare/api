import resend

from shared import db, settings

resend.api_key = settings.get().resend_api_key

async def send_confirmation(email: str):
    code: str = await db.query_one('select MakeVerificationCode(%s)', (email,))

    resend.Emails.send({
        'from': 'Pacuare Reserve <support@farthergate.com>',
        'to': [email],
        'subject': 'Login Confirmation',
        'text': """
        Please use the code {} to log into Pacuare Reserve.

        Por favor usar la clave {} para iniciar en Pacuare Reserve.
        """.format(code, code)
    })
