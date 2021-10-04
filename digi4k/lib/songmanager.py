from typing import Optional
from digi4k.lib.inputmanager import InputManager
from digi4k.lib.objects.keybinder import KeyBinder
from digi4k.lib.objects.note import ChartNote, Song

# SongManager has a few jobs: applies hits to notes, applies misses to notes,
# deals with note side-effects (HP drain/gain, etc), calculating per-note and
# and full-song accuracy... it might be too much but hey, we can split this up
# later.


class SongManager:
    def __init__(self, song: Song, inputmanager: InputManager, keybinder: KeyBinder, hitwindow: Optional[tuple[float, float]] = None):
        self.song = song
        self.input = inputmanager
        self.keybinder = keybinder

        if hitwindow is None:
            front_end = (166 * (2 / 3)) / 1000
            back_end = (166 * (1 / 3)) / 1000
        else:
            front_end, back_end = hitwindow
        self.front_end = front_end
        self.back_end = back_end

        self.lanemap = {
            self.keybinder.left: 0,
            self.keybinder.down: 1,
            self.keybinder.up: 2,
            self.keybinder.right: 3
        }

        self.hits = 0
        self.misses = 0

    def _try_hit_note(self, current_time: float, chart_idx: int = 0) -> int:
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

        hits = len(notes_hit)
        return hits

    def update(self, current_time: float):
        # Try to hit some notes
        self.hits += self._try_hit_note(current_time)
        # TODO: Miss notes, calc accuracy, apply HP
