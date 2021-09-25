from typing import List, Literal

import pygame
from pygame.color import Color
import pygame.draw
import pygame.transform
from pygame import Rect
from pygame.constants import SRCALPHA
from pygame.surface import Surface

MISSING_TEXTURE = Surface((120, 120))
MISSING_TEXTURE.fill(0xFF00FF)
MISSING_TEXTURE.fill(0x000000, Rect(60, 0, 60, 60))
MISSING_TEXTURE.fill(0x000000, Rect(0, 60, 60, 60))

BLACK = Color(0x000000FF)

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


class Note:
    valid_flags = ["normal"]

    def __init__(self, lane: Literal[0, 1, 2, 3], position: float, length: float = 0.0, flag: str = "normal"):
        self.lane = lane
        self.position = position
        self.length = length
        self.flag = flag

    def __str__(self) -> str:
        flag = "" if self.flag == "normal" else self.flag.title() + " "
        arrow = arrowmap[self.lane]
        pos = f" P {round(self.position, 4)}"
        length = "" if self.length == 0 else f" L {round(self.length, 4)}"
        return f"<Note {flag}{arrow}{pos}{length}>"

    @property
    def sprite(self) -> Surface:
        surf = Surface((120, 120), flags = SRCALPHA)
        if self.flag not in self.valid_flags:
            return MISSING_TEXTURE

        color = colormap[self.lane]
        pygame.draw.polygon(surf, color, up_arrow_shape, 0)
        pygame.draw.lines(surf, BLACK, True, up_arrow_shape, 6)
        surf = pygame.transform.rotate(surf, anglemap[self.lane])
        return surf


class DisplayNote:
    def __init__(self, note: Note):
        self.note = note
        self.hit_time = None

    @property
    def lane(self):
        return self.note.lane

    @property
    def position(self):
        return self.note.position

    @property
    def length(self):
        return self.note.length

    @property
    def flag(self):
        return self.note.flag

    @property
    def sprite(self):
        return self.note.sprite

    def __str__(self) -> str:
        return self.note.__str__().replace("Note", "DisplayNote")


class Highway:
    def __init__(self, notes: List[Note], size = (480, 720)) -> None:
        self.notes = notes
        self.size = size
        self.viewport_size = 0.75  # 750ms

        self.current_pos = 0.0

        self._image = Surface(self.size, flags = pygame.SRCALPHA)

    @property
    def sprite_size(self):
        return self.size[0] // 4

    @property
    def px_per_sec(self):
        return self.size[1] / self.viewport_size

    @property
    def current_notes(self):
        return [note for note in self.notes if self.current_pos - 0.1 < note.pos <= self.current_pos + self.viewport_size]

    def update(self, time):
        self.current_pos = time
        for note in self.current_notes:
            pass
