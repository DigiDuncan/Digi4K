from __future__ import annotations
from typing import TYPE_CHECKING

from importlib.resources import path

from pygame.color import Color
from pygame.constants import K_SPACE

from digi4k.lib.objects.inputparser import InputParser
from digi4k.lib.objects.keybinder import KeyBinder

if TYPE_CHECKING:
    from digi4k.main import Game

import json
from importlib.resources import files

from nygame import music

import digi4k.data.charts.test
from digi4k.lib.draw_objects import EventViewer, Highway
from digi4k.lib.inputmanager import InputManager
from digi4k.lib.objects.note import Song
from digi4k.lib import ptext


class GameManager:
    def __init__(self, game: Game):
        self.game = game
        self.song_file = j = json.loads(files(digi4k.data.charts.test).joinpath("test.json").read_text())
        self.song = Song.from_json(j)
        self.highway_p1 = Highway(self.song.charts[0])
        self.highway_p2 = Highway(self.song.charts[1])
        music.play(files(digi4k.data.charts.test).joinpath("Inst.ogg"))

        self.input = InputManager()
        self.inputparser = InputParser(0, 0)

        self.keybinder = KeyBinder()

        self.eventviewer = EventViewer(self.song.events)

        self.hits = 0
        self.last_acc = None

        with path(digi4k.data.fonts, "debug.ttf") as fp:
            self.font = fp

    def update(self, events: list):
        now = music.elapsed
        self.input.update(events)
        self.eventviewer.update(now)

        if K_SPACE in self.input.justPressed:
            music.playpause()

        lanemap = {
            self.keybinder.left: 0,
            self.keybinder.down: 1,
            self.keybinder.up: 2,
            self.keybinder.right: 3
        }

        lanes = [lanemap[k] for k in self.input.justPressed if k in lanemap]

        hits, accs = self.inputparser.try_hit_note(now, lanes, self.song.charts[0])
        self.hits += hits
        ptext.draw(str(self.hits), midtop = self.game.surface.get_rect().midtop, fontname = self.font, fontsize = 100, color = Color(0x000000), surf = self.game.surface)
        if accs:
            self.last_acc = accs[-1]
        if self.last_acc is not None:
            acc_str = str(round(self.last_acc * 1000)) + "ms"
            ptext.draw(acc_str, midtop = (self.game.surface.get_rect().centerx, 100), fontname = self.font, fontsize = 60, color = Color(0x000000), surf = self.game.surface)

        # Draws
        self.highway_p1.update(now)
        self.highway_p2.update(now)
        highway_p1_rect = self.highway_p1.image.get_rect()
        highway_p1_rect.midright = self.game.surface.get_rect().midright
        highway_p2_rect = self.highway_p2.image.get_rect()
        highway_p2_rect.midleft = self.game.surface.get_rect().midleft
        eventviewer_rect = self.eventviewer.image.get_rect()
        eventviewer_rect.center = self.game.surface.get_rect().center
        self.game.surface.blit(self.highway_p1.image, highway_p1_rect)
        self.game.surface.blit(self.highway_p2.image, highway_p2_rect)
        self.game.surface.blit(self.eventviewer.image, eventviewer_rect)
