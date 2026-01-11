from typing import Annotated

from fastapi import Depends
from sprites import SpritesClient

from shared import settings
from shared.settings import Settings


def client(settings: Annotated[Settings, Depends(settings.get)]):
    return SpritesClient(settings.sprites_token)


GetSpritesClient = Annotated[SpritesClient, Depends(client)]
