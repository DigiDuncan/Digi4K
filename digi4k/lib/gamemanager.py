from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from digi4k.main import Game

from pygame import K_LEFT, K_RIGHT, K_LEFTBRACKET, K_RIGHTBRACKET

from digi4k.lib.inputmanager import InputManager
from digi4k.lib import ptext

from digi4k.lib.draw_objects import DisplayNote, Note


class GameManager:
    def __init__(self, game: Game):
        self.game = game
        self.lanes = [0, 1, 2, 3]
        self.flags = ["normal", "bomb", "death", "gold", "unknown"]

        self.current_lane: int = 0
        self.current_flag: int = 0

        self.input = InputManager()
        self.old_out = ""

    def update(self, events: list):
        self.input.update(events)
        # if self.input.justPressed or self.input.justReleased:
        #     print(self.input)

        if K_LEFT in self.input.justPressed:
            self.current_lane -= 1
        elif K_RIGHT in self.input.justPressed:
            self.current_lane += 1
        elif K_LEFTBRACKET in self.input.justPressed:
            self.current_flag -= 1
        elif K_RIGHTBRACKET in self.input.justPressed:
            self.current_flag += 1

        self.current_lane %= len(self.lanes)
        self.current_flag %= len(self.flags)
        lane = self.lanes[self.current_lane]
        flag = self.flags[self.current_flag]

        note = DisplayNote(Note(lane, 0, 0, flag = flag))
        note_sprite = note.sprite
        note_rect = note_sprite.get_rect()
        note_rect.center = self.game.surface.get_rect().center
        self.game.surface.blit(note_sprite, note_rect)
        ptext.draw(f"{self.flags[self.current_flag]} {self.current_lane}", bottomleft=note_rect.move(0, -10).topleft, sysfontname="Lato Medium", fontsize=48, surf=self.game.surface)
