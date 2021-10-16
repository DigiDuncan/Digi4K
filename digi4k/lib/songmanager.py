from typing import Optional, Union

from importlib.resources import files

from pygame.color import Color
from pygame.rect import Rect
from pygame.surface import Surface

from digi4k.lib.inputmanager import InputManager
from digi4k.lib.objects.keybinder import KeyBinder
from digi4k.lib.objects.note import ChartNote, Song
from digi4k.lib import ptext
import digi4k.data.fonts

# SongManager has a few jobs: applies hits to notes, applies misses to notes,
# deals with note side-effects (HP drain/gain, etc), calculating per-note and
# and full-song accuracy... it might be too much but hey, we can split this up
# later.


class SongManager:
    def __init__(self, song: Song, inputmanager: InputManager, keybinder: KeyBinder, hitwindow: Optional[tuple[float, float]] = None):
        # Input params
        self.song = song
        self.input = inputmanager
        self.keybinder = keybinder

        # Hit window
        if hitwindow is None:
            front_end = (166 * (2 / 3)) / 1000
            back_end = (166 * (1 / 3)) / 1000
        else:
            front_end, back_end = hitwindow
        self.front_end = front_end
        self.back_end = back_end

        # Lanemap
        self.lanemap = {
            self.keybinder.left: 0,
            self.keybinder.down: 1,
            self.keybinder.up: 2,
            self.keybinder.right: 3
        }

        # Hit / miss count
        self.hits = 0
        self.misses = 0

        # Modchart stuff [unused currently, gotta calc these]
        self.current_time = 0
        self.current_step = 0
        self.current_beat = 0
        self.current_player = None

        self.font = files(digi4k.data.fonts) / "debug.ttf"

        self.last_acc: Union[float, None] = None

    def _try_hit_note(self, current_time: float, chart_idx: int = 0) -> list[ChartNote]:
        lanes_to_hit = {lane for key, lane in self.lanemap.items() if key in self.input.justPressed}
        chart = self.song.charts[chart_idx]

        notes_hit: list[ChartNote] = []
        for note in chart.get_hittable_notes(current_time, self.front_end, self.back_end):
            if not lanes_to_hit:
                break
            if note.lane in lanes_to_hit:
                lanes_to_hit.remove(note.lane)
                notes_hit.append(note)

        for note in notes_hit:
            note.hit = True
            note.hit_time = current_time

        return notes_hit

    def update(self, current_time: float):
        # Try to hit some notes
        hit_notes = self._try_hit_note(current_time)
        self.hits += len(hit_notes)
        if hit_notes:
            self.last_acc = hit_notes[-1].hit_offset
        # TODO: Miss notes, apply HP

    def render_to(self, surf: Surface, dest: Rect):
        ptext.draw(str(self.hits), midtop = dest.midtop, fontname = self.font, fontsize = 100, color = Color(0x000000), surf = surf)
        if self.last_acc is not None:
            acc_ms = round(self.last_acc * 1000)
            ptext.draw(f"{acc_ms}ms", midtop = dest.move(0, 75).midtop, fontname = self.font, fontsize = 60, color = Color(0x000000), surf = surf)
