from logging import info
from typing import Annotated

from fastapi import APIRouter, Depends
from sprites import URLSettings
from sprites.services import create_service, start_service
from sprites.sprite import Sprite

from api.v1.auth.utils import GetUserDatabase
from shared.sprites import GetSpritesClient

router = APIRouter()

def sprite_name(db_name: GetUserDatabase) -> str:
    return 'pacuare-' + db_name.replace('_', '-')

@router.post('/')
def create(sprites: GetSpritesClient, name: Annotated[str, Depends(sprite_name)]):
    print(f'creating sprite {name}')
    sprites.create_sprite(name)

    sprite: Sprite = sprites.sprite(name)
    sprite.update_url_settings(URLSettings('public'))

    sprite.command("pip", "install", "marimo").run()
    create_service(sprite, "marimo", "python3", ['-m', 'marimo', 'edit', '-p', '8080'], http_port=8080)
    start_service(sprite, "marimo", 0)

    return {'name': name, 'url': sprite.url}
