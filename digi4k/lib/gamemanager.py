from __future__ import annotations

import json
from importlib.resources import files
from pygame.rect import Rect

from pygame.surface import Surface
from pygame.constants import K_SPACE
from nygame import music

from digi4k.lib.objects.keybinder import KeyBinder
import digi4k.data.charts.test
import digi4k.data.fonts
from digi4k.lib.draw_objects import EventViewer, Highway
from digi4k.lib.inputmanager import InputManager
from digi4k.lib.songmanager import SongManager
from digi4k.lib.objects.note import Song


class GameManager:
    def __init__(self):
        j = json.loads(files(digi4k.data.charts.test).joinpath("test.json").read_text())
        self.song = Song.from_json(j)
        self.highway_p1 = Highway(self.song.charts[0])
        self.highway_p2 = Highway(self.song.charts[1])
        music.play(files(digi4k.data.charts.test).joinpath("Inst.ogg"))

        self.input = InputManager()
        self.keybinder = KeyBinder()
        self.eventviewer = EventViewer(self.song.events)

        self.songmanager = SongManager(self.song, self.input, self.keybinder)

        self.font = files(digi4k.data.fonts) / "debug.ttf"

    def update(self, events: list):
        self.input.update(events)

        if K_SPACE in self.input.justPressed:
            music.playpause()

        lanekeys = [
            self.keybinder.left,
            self.keybinder.down,
            self.keybinder.up,
            self.keybinder.right
        ]
        self.highway_p1.lanes_pressed = [k in self.input.pressed for k in lanekeys]

        now = music.elapsed
        self.eventviewer.update(now)
        self.songmanager.update(now)
        self.highway_p1.update(now)
        self.highway_p2.update(now)

    def render_to(self, surf: Surface):
        surf_rect = surf.get_rect()

        highway_p1_rect = self.highway_p1.get_rect()
        highway_p1_rect.midright = surf_rect.midright
        self.highway_p1.render_to(surf, highway_p1_rect)

        highway_p2_rect = self.highway_p2.get_rect()
        highway_p2_rect.midleft = surf_rect.midleft
        self.highway_p2.render_to(surf, highway_p2_rect)

        eventviewer_rect = self.eventviewer.get_rect()
        eventviewer_rect.center = surf_rect.center
        self.eventviewer.render_to(surf, eventviewer_rect)

        songmanager_rect = Rect(0, 0, 0, 0)
        songmanager_rect.midtop = surf_rect.midtop
        self.songmanager.render_to(surf, songmanager_rect)
