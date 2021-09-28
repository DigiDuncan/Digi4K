import pygame.key

from pygame import KEYDOWN, KEYUP
from pygame.event import Event


class InputManager:
    def __init__(self):
        self.pressed = set()
        self.justPressed = set()
        self.justReleased = set()

    def update(self, events: list[Event]):
        self.justPressed.clear()
        self.justReleased.clear()
        for e in events:
            if e.type == KEYDOWN:
                self.press(e.key)
            elif e.type == KEYUP:
                self.release(e.key)

    def press(self, key: int):
        self.justPressed.add(key)
        self.pressed.add(key)

    def release(self, key: int):
        self.justReleased.add(key)
        self.pressed.discard(key)

    @property
    def has_changes(self):
        return bool(self.justPressed or self.justReleased)

    def __str__(self):
        keys = sorted(self.pressed | self.justReleased)
        return " ".join(key_str(k, k in self.justPressed, k in self.justReleased) for k in keys)


def key_str(key: int, pressed: bool, released: bool) -> str:
    if pressed:
        prefix = "🗹"
    elif released:
        prefix = "🗵"
    else:
        prefix = "⬚"

    return prefix + pygame.key.name(key)
