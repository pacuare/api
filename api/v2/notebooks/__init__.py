import json
from typing import Annotated

from fastapi import APIRouter, Depends
from httpx import NetworkError
from sprites import SpriteError, URLSettings
from sprites.sprite import Sprite

from api.v1.auth.utils import GetUserDatabase
from shared.sprites import GetSpritesClient
from shared.sprites.services import Service

router = APIRouter()


def sprite_name(db_name: GetUserDatabase) -> str:
    return "pacuare-" + db_name.replace("_", "-")


GetSpriteName = Annotated[str, Depends(sprite_name)]


@router.post("/")
async def create_sprite(sprites: GetSpritesClient, name: GetSpriteName):
    print(f"creating sprite {name}")

    sprite: Sprite

    try:
        sprite = sprites.create_sprite(name)
    except SpriteError:
        print(f"failed to create sprite {name}; most likely it already exists")
        sprite = sprites.get_sprite(name)

    sprite.update_url_settings(URLSettings("public"))

    sprite.command("pip", "install", "marimo").run()
    stream = sprite.create_checkpoint("basic-marimo")

    for msg in stream:
        print(json.dumps({"type": msg.type, "data": msg.data}))

    svc = Service(
        sprite,
        "marimo",
        "python3",
        "-m",
        "marimo",
        "edit",
        "-p",
        "8080",
    )
    await svc.start()

    return {"name": name, "url": sprite.url}


@router.delete("/")
def delete_sprite(sprites: GetSpritesClient, name: GetSpriteName) -> str:
    sprites.delete_sprite(name)
    return name


@router.post("/reset")
def reset_sprite(sprites: GetSpritesClient, name: GetSpriteName) -> str:
    sprite: Sprite = sprites.sprite(name)
    cp = sprite.list_checkpoints("basic-marimo")
    sprite.restore_checkpoint(cp.id)
    return name
