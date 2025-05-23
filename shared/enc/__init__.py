from cryptography.fernet import Fernet
from shared import settings

f = Fernet(settings.get().fernet_key)
