from importlib.resources import path

import pygame
import pygame.draw
import pygame.image
import pygame.transform
from pygame import Rect
from pygame.color import Color
from pygame.constants import SRCALPHA
from pygame.surface import Surface

import digi4k.data.fonts
import digi4k.data.images.debug
from digi4k.lib import ptext
from digi4k.lib.objects.note import Chart, ChartEvent, ChartNote

MISSING_TEXTURE = Surface((120, 120))
MISSING_TEXTURE.fill(0xFF00FF)
MISSING_TEXTURE.fill(0x000000, Rect(60, 0, 60, 60))
MISSING_TEXTURE.fill(0x000000, Rect(0, 60, 60, 60))

BLACK = Color(0x000000FF)
CLEAR = Color(0x00000000)

arrowmap = ["⬅", "⬇", "⬆", "➡"]
colormap = [Color(0xFF00FFFF),
            Color(0x00FFFFFF),
            Color(0x00FF00FF),
            Color(0xFF0000FF)]
anglemap = [90, 180, 0, -90]
up_arrow_shape = [
    (60, 4),
    (4, 60),
    (40, 60),
    (40, 116),
    (80, 116),
    (80, 60),
    (116, 60)
]


class DisplayNote:
    valid_flags = ["normal"]
    cache = {}

    def __init__(self, note: ChartNote):
        self.note = note

    @property
    def lane(self):
        return self.note.lane

    @property
    def pos(self):
        return self.note.pos

    @property
    def length(self):
        return self.note.length

    @property
    def flag(self):
        return self.note.flag

    @property
    def hit(self):
        return self.note.hit

    @property
    def hit_time(self):
        return self.note.hit_time

    @property
    def missed(self):
        return self.note.missed

    # This will need to be adjusted later to account for, like, everything.
    @property
    def caching_key(self):
        return self.note.lane, self.note.length, self.note.flag, self.note.hit, self.note.missed

    @property
    def sprite(self):
        if self.caching_key in self.cache:
            return self.cache[self.caching_key]

        surf = Surface((120, 120), flags = SRCALPHA)
        if self.flag not in self.valid_flags:
            return MISSING_TEXTURE

        if self.flag == "normal":
            color = colormap[self.lane]
            outline = Color(0x000000FF)
        elif self.flag == "bomb":
            color = Color(0x000000FF)
            outline = Color(0xAA0000FF)
        elif self.flag == "death":
            color = Color(0x000000FF)
            outline = Color(0xFFFFFFFF)
        elif self.flag == "gold":
            color = Color(0xAAAA00FF)
            outline = Color(0xAA6600FF)

        pygame.draw.polygon(surf, color, up_arrow_shape, 0)
        pygame.draw.lines(surf, outline, True, up_arrow_shape, 6)
        surf = pygame.transform.rotate(surf, anglemap[self.lane])

        if self.hit:
            surf.set_alpha(100)

        self.cache[self.caching_key] = surf
        return surf

    def __repr__(self) -> str:
        return self.note.__repr__().replace("Note", "DisplayNote")

    def __str__(self) -> str:
        return self.note.__str__().replace("Note", "DisplayNote")


class Highway:
    def __init__(self, chart: Chart, size = (480, 720)) -> None:
        self.notes = chart.notes
        self.size = size
        self.viewport_size = 0.75  # 750ms
        self.y_buffer = 50

        self.current_pos = 0.0

        self.image = Surface(self.size, flags = pygame.SRCALPHA)

    @property
    def sprite_size(self):
        return self.size[0] // 4

    @property
    def zero(self):
        return self.y_buffer + (self.sprite_size / 2)

    @property
    def px_per_sec(self):
        return self.size[1] / self.viewport_size

    @property
    def current_notes(self):
        # This isn't a good way of doing this
        return [note for note in self.notes if self.current_pos - 1 < note.pos <= self.current_pos + self.viewport_size]

    def get_note_pos(self, dn: DisplayNote):
        x = dn.lane * self.sprite_size
        offset = self.current_pos - dn.pos
        offset = -offset
        y = (offset * self.px_per_sec) + self.zero
        return (x, y)

    def update(self, time):
        self.image.fill(BLACK)
        pygame.draw.line(self.image, Color(0xFF0000FF), (0, self.zero), (self.size[1], self.zero), 3)
        self.current_pos = time
        display_notes = [DisplayNote(note) for note in self.current_notes]
        for note in display_notes:
            pos = self.get_note_pos(note)
            self.image.blit(note.sprite, pos)


class EventViewer:
    def __init__(self, events: list[ChartEvent]):
        self.events: list[ChartEvent] = sorted(events)
        self._image = Surface((64, 64), flags = SRCALPHA)
        self.module = digi4k.data.images.debug

    def event_to_icon(self, event: ChartEvent) -> Surface:
        if event.name == "camera_focus" and event.data == {"focus": "player1"}:
            return "cam_p1"
        elif event.name == "camera_focus" and event.data == {"focus": "player2"}:
            return "cam_p2"
        elif event.name == "change_bpm":
            return "bpm"
        return "missing"

    def update(self, time: float):
        self._image.fill(CLEAR)
        eventlist = [e for e in self.events if e.pos <= time][::-1]
        if not eventlist:
            return
        event = eventlist[0]
        current_offset = round(time - event.pos, 3)

        with path(digi4k.data.images.debug, self.event_to_icon(event) + ".png") as ip:
            iconpath = ip
        with path(digi4k.data.fonts, "debug.ttf") as fp:
            fontpath = fp

        icon = pygame.image.load(iconpath)
        if event.name == "change_bpm":
            bpmtext = ptext.draw(str(round(event.data["bpm"], 2)), fontsize = 12, fontname = fontpath, color = Color(0xAA00AA), topleft = (0, 16))
            icon.blit(*bpmtext)
        self._image.blit(icon, (16, 0))
        text = ptext.drawbox(str(current_offset), (0, 32, 64, 32), fontname = fontpath, color = BLACK)
        self._image.blit(*text)

    @property
    def image(self) -> Surface:
        return pygame.transform.scale(self._image, (128, 128))
