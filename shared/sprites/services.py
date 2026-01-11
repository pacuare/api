"""
This module implements a basic version of the Sprites Services API until the real one stops returning 404.
"""

from typing import Any

from sprites import Sprite
from sprites.exec import Cmd
from sprites.websocket import WSCommand


class Service:
    _sprite: Sprite
    args: tuple[str, ...]
    kwargs: dict[str, Any]

    def __init__(self, sprite: Sprite, *args: str, **kwargs):
        self._sprite = sprite
        self.args = args
        self.kwargs = kwargs

    async def start(self):
        cmd: Cmd = self._sprite.command(*self.args, **self.kwargs)
        wscmd = WSCommand(cmd)
        await wscmd.start()
