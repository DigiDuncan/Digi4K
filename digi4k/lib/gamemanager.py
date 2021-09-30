from __future__ import annotations
from typing import TYPE_CHECKING

from digi4k.lib.objects.note import Chart

if TYPE_CHECKING:
    from digi4k.main import Game

from digi4k.lib.inputmanager import InputManager

from digi4k.lib.draw_objects import Highway
from importlib.resources import files
import json

import digi4k.data.tutorial

from nygame import music


class GameManager:
    def __init__(self, game: Game):
        self.game = game
        self.chart_file = j = json.loads(files(digi4k.data.tutorial).joinpath("tutorial-hard.json").read_text())
        self.chart = Chart.from_json(j)
        self.highway = Highway(self.chart)
        music.play(files(digi4k.data.tutorial).joinpath("Tutorial_Inst.ogg"))

        self.input = InputManager()

    def update(self, events: list):
        now = music.elapsed
        self.input.update(events)
        self.highway.update(now)
        highway_rect = self.highway._image.get_rect()
        highway_rect.center = self.game.surface.get_rect().center
        self.game.surface.blit(self.highway._image, (0, 0))
