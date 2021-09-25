from typing import List, Literal

import pygame
import pygame.draw
import pygame.transform
from pygame import Rect
from pygame.constants import SRCALPHA
from pygame.surface import Surface

MISSING_TEXTURE = Surface((120, 120))
MISSING_TEXTURE.fill(0xFF00FF)
MISSING_TEXTURE.fill(0x000000, Rect(60, 0, 60, 60))
MISSING_TEXTURE.fill(0x000000, Rect(0, 60, 60, 60))

arrowmap = ["⬅", "⬇", "⬆", "➡"]
colormap = [0xFF00FF, 0x00FFFF, 0x00FF00, 0xFF0000]
anglemap = [-90, 180, 0, 90]
up_arrow_shape = [(43, 112), (76, 112), (76, 60), (97, 36), (112, 60), (60, 8), (8, 60), (23, 36), (43, 60)]


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
        return f"<{flag}{arrow}{pos}{length}>"

    @property
    def sprite(self) -> Surface:
        surf = Surface((120, 120), flags = SRCALPHA)
        if self.flag not in self.valid_flags:
            return MISSING_TEXTURE

        color = colormap[self.lane]
        pygame.draw.polygon(surf, (0xFF, 0x00, 0xFF, 0xFF), up_arrow_shape, 0)
        # pygame.draw.polygon(surf, 0x000000FF, up_arrow_shape, 6)
        pygame.transform.rotate(surf, anglemap[self.lane])
        return surf


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
