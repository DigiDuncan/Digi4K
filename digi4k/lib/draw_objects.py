from functools import cache
from typing import Optional, Union

from importlib.resources import files

import pygame
import pygame.draw
import pygame.image
import pygame.transform
from pygame.rect import Rect
from pygame.color import Color
from pygame.constants import SRCALPHA
from pygame.surface import Surface

import digi4k.data.fonts
import digi4k.data.images.debug
from digi4k.lib import ptext
from digi4k.lib.objects.note import ChangeBpmEvent, Chart, ChartEvent, ChartNote, Flag, Flags

MISSING_TEXTURE = Surface((120, 120))
MISSING_TEXTURE.fill(Color(0xFF00FF))
MISSING_TEXTURE.fill(Color(0x000000), Rect(60, 0, 60, 60))
MISSING_TEXTURE.fill(Color(0x000000), Rect(0, 60, 60, 60))

BLACK = Color(0x000000FF)
CLEAR = Color(0x00000000)

arrowmap = ["⬅", "⬇", "⬆", "➡"]
colormap = [
    Color(0xFF00FFFF),
    Color(0x00FFFFFF),
    Color(0x00FF00FF),
    Color(0xFF0000FF)
]
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


def draw_sprite(lane: int, length: float, flag: Flag, hit: bool, missed: bool):
    return draw_sprite_cached(lane, flag, hit)


@cache
def draw_sprite_cached(lane: int, flag: Flag, hit: bool):
    if flag not in Flags:
        return MISSING_TEXTURE

    if flag == Flags.NORMAL:
        color = colormap[lane]
        outline = Color(0x000000FF)
    elif flag == Flags.BOMB:
        color = Color(0x000000FF)
        outline = Color(0xAA0000FF)
    elif flag == Flags.DEATH:
        color = Color(0x000000FF)
        outline = Color(0xFFFFFFFF)
    elif flag == Flags.GOLD:
        color = Color(0xAAAA00FF)
        outline = Color(0xAA6600FF)

    surf = Surface((120, 120), flags = SRCALPHA)
    pygame.draw.polygon(surf, color, up_arrow_shape, 0)
    pygame.draw.lines(surf, outline, True, up_arrow_shape, 6)
    surf = pygame.transform.rotate(surf, anglemap[lane])

    if hit:
        surf.set_alpha(100)

    return surf


class DisplayNote:
    def __init__(self, note: ChartNote):
        self.note = note
        self.pos = self.note.pos
        self.lane = self.note.lane
        self.vanilla_sprite = draw_sprite(note.lane, note.length, note.flag, False, False)
        self.hit_sprite = draw_sprite(note.lane, note.length, note.flag, True, False)
        self.miss_sprite = draw_sprite(note.lane, note.length, note.flag, False, True)

    @property
    def sprite(self):
        if self.note.hit:
            return self.hit_sprite
        elif self.note.missed:
            return self.miss_sprite
        else:
            return self.vanilla_sprite

    def __repr__(self) -> str:
        return "<DisplayNote " + repr(self.note) + " >"

    def __str__(self) -> str:
        return "<DisplayNote " + str(self.note) + " >"


class Highway:
    def __init__(self, chart: Chart, size: tuple[int, int] = (480, 720)) -> None:
        self.notes = [DisplayNote(note) for note in chart.notes]
        self.size = size
        self.sprite_size = (self.w // 4, self.w // 4)
        self.rel_sprite_size = (self.sprite_size[0] / self.size[0], self.sprite_size[1] / self.size[1])

        self.rel_y_buffer: float = 100 / 720

        self.y_buffer: int = int(self.rel_y_buffer * self.h)

        self.viewport_size = 0.75  # 750ms

        self.current_notes: list[DisplayNote] = []
        self._next_note: Optional[DisplayNote] = None
        self.pop_next()

    @property
    def w(self):
        return self.size[0]

    @property
    def h(self):
        return self.size[1]

    def pop_next(self):
        if self._next_note is not None:
            self.current_notes.append(self._next_note)
        try:
            self._next_note = self.notes.pop(0)
        except IndexError:
            self._next_note = None

    def update_current_notes(self):
        while self._next_note is not None and self.get_note_rect(self._next_note).top < self.h:
            self.pop_next()

        while self.current_notes and self.get_note_rect(self.current_notes[0]).bottom < 0:
            self.current_notes.pop(0)

    def get_rect(self):
        return Rect(0, 0, self.w, self.h)

    def get_note_rect(self, note: DisplayNote) -> Rect:
        w, h = self.sprite_size

        x = note.lane * w

        offset = note.pos - self.time   # negative past, positive future

        rely = (offset) / self.viewport_size
        y = rely * self.h
        y -= h / 2
        y += self.y_buffer

        return Rect(x, int(y), w, h)

    def update(self, time: float):
        self.time = time
        self.update_current_notes()

    def render_to(self, surf: Surface, dest: Rect):
        surf.fill(BLACK, dest)
        linerect = Rect(0, self.y_buffer, self.w, 0)
        linerect.move_ip(dest.x, dest.y)
        pygame.draw.line(surf, Color(0xFF0000FF), linerect.topleft, linerect.topright, 3)
        for note in self.current_notes:
            note_rect = self.get_note_rect(note)
            surf.blit(note.sprite, note_rect.move(dest.topleft))


class EventViewer:
    def __init__(self, events: list[ChartEvent]):
        self.events: list[ChartEvent] = events.copy()
        self._buff = Surface((64, 64), flags = SRCALPHA)
        self._buff2 = Surface((128, 128), flags = SRCALPHA)
        self.icon_images = {name: pygame.image.load(files(digi4k.data.images.debug) / f"{name}.png").convert_alpha() for name in ["missing", "bpm", "cam_p1", "cam_p2"]}
        self._font = files(digi4k.data.fonts) / "debug.ttf"
        self.current_offset = None
        self._next_event: Union[ChartEvent, None] = None
        self.curr_event: Union[ChartEvent, None] = None
        self.pop_next()

    def pop_next(self):
        self.curr_event = self._next_event
        try:
            self._next_event = self.events.pop(0)
        except IndexError:
            self._next_event = None

    def update_curr_event(self, time: float):
        while self._next_event is not None and self._next_event.pos <= time:
            self.pop_next()

    def update(self, time: float):
        self.update_curr_event(time)
        if self.curr_event is None:
            self.current_offset = None
            return
        self.current_offset = round(time - self.curr_event.pos, 3)

    def get_rect(self) -> Rect:
        return self._buff2.get_rect()

    def render_to(self, surf: Surface, dest: Union[tuple[int, int], Rect]):
        if self.curr_event is None:
            return

        self._buff.fill("clear")

        self._buff.blit(self.icon_images[self.curr_event.icon], (16, 0))
        # BPM events are special, put BPM on icon
        if isinstance(self.curr_event, ChangeBpmEvent):
            ptext.draw(str(round(self.curr_event.bpm, 2)), fontsize = 12, fontname = self._font, color = Color(0xAA00AA), topleft = (16, 16), surf = self._buff)

        ptext.drawbox(str(self.current_offset), (0, 32, 64, 32), fontname = self._font, color = BLACK, surf = self._buff)
        pygame.transform.scale2x(self._buff, self._buff2)
        surf.blit(self._buff2, dest)
