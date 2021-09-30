from __future__ import annotations
from typing import TYPE_CHECKING

from digi4k.lib.objects.inputparser import InputParser
from digi4k.lib.objects.keybinder import KeyBinder

if TYPE_CHECKING:
    from digi4k.main import Game

import json
from importlib.resources import files

from nygame import music

import digi4k.data.tutorial
from digi4k.lib.draw_objects import Highway
from digi4k.lib.inputmanager import InputManager
from digi4k.lib.objects.note import Song


class GameManager:
    def __init__(self, game: Game):
        self.game = game
        self.song_file = j = json.loads(files(digi4k.data.tutorial).joinpath("tutorial-hard.json").read_text())
        self.song = Song.from_json(j)
        self.highway_p1 = Highway(self.song.charts[0])
        self.highway_p2 = Highway(self.song.charts[1])
        music.play(files(digi4k.data.tutorial).joinpath("Tutorial_Inst.ogg"))

        self.input = InputManager()
        self.inputparser = InputParser(0, 0)

        self.keybinder = KeyBinder()

    def update(self, events: list):
        now = music.elapsed
        self.input.update(events)

        lanemap = {
            self.keybinder.left: 0,
            self.keybinder.down: 1,
            self.keybinder.up: 2,
            self.keybinder.right: 3
        }

        lanes = [lanemap[k] for k in self.input.justPressed]

        self.inputparser.try_hit_note(now, lanes, self.song.charts[0])

        # Draws
        self.highway_p1.update(now)
        self.highway_p2.update(now)
        highway_p1_rect = self.highway_p1._image.get_rect()
        highway_p1_rect.midright = self.game.surface.get_rect().midright
        highway_p2_rect = self.highway_p2._image.get_rect()
        highway_p2_rect.midleft = self.game.surface.get_rect().midleft
        self.game.surface.blit(self.highway_p1._image, highway_p1_rect)
        self.game.surface.blit(self.highway_p2._image, highway_p2_rect)
