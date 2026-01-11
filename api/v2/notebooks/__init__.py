from typing import Annotated

from fastapi import APIRouter, Depends
from httpx import NetworkError
from sprites import URLSettings
from sprites.services import create_service, start_service
from sprites.sprite import Sprite

from api.v1.auth.utils import GetUserDatabase
from shared.sprites import GetSpritesClient

router = APIRouter()


def sprite_name(db_name: GetUserDatabase) -> str:
    return "pacuare-" + db_name.replace("_", "-")


GetSpriteName = Annotated[str, Depends(sprite_name)]


@router.post("/")
def create_sprite(sprites: GetSpritesClient, name: GetSpriteName):
    print(f"creating sprite {name}")

    try:
        sprites.create_sprite(name)
    except NetworkError:
        print(f"failed to create sprite {name}; most likely it already exists")

    sprite: Sprite = sprites.sprite(name)
    sprite.update_url_settings(URLSettings("public"))

    sprite.command("pip", "install", "marimo").run()
    sprite.create_checkpoint("basic-marimo")

    create_service(
        sprite,
        "marimo",
        "python3",
        ["-m", "marimo", "edit", "-p", "8080"],
        http_port=8080,
    )
    start_service(sprite, "marimo", 0)

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
