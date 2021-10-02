from digi4k.lib.inputmanager import InputManager
from digi4k.lib.objects.keybinder import KeyBinder
from digi4k.lib.objects.note import ChartNote, Song

# SongManager has a few jobs: applies hits to notes, applies misses to notes,
# deals with note side-effects (HP drain/gain, etc), calculating per-note and
# and full-song accuracy... it might be too much but hey, we can split this up
# later.


class SongManager:
    def __init__(self, song: Song, inputmanager: InputManager, keybinder: KeyBinder, hitwindow: tuple[float, float] = None):
        self.song = song
        self.input = inputmanager
        self.keybinder = keybinder
        self.hitwindow = hitwindow if hitwindow is not None else (166 * (2 / 3), 166 * (1 / 3))

        self.lanemap = {
            self.keybinder.left: 0,
            self.keybinder.down: 1,
            self.keybinder.up: 2,
            self.keybinder.right: 3
        }

        self.hits = 0
        self.misses = 0

    @property
    def front_end(self):
        return self.hitwindow[0]

    @property
    def back_end(self):
        return self.hitwindow[1]

    def _try_hit_note(self, current_time: float, chart_idx: int = 0) -> int:
        lanes = [self.lanemap[k] for k in self.input.justPressed if k in self.lanemap]
        chart = self.song.charts[chart_idx]
        notes = chart.notes
        hits = 0
        for lane in lanes:
            good_notes: list[ChartNote] = sorted([note for note in notes if note.lane == lane and note.hittable(current_time, (self.front_end, self.back_end))])
            if good_notes:
                good_notes[0].hit = True
                good_notes[0].hit_time = current_time
                hits += 1
        return hits

    def update(self, current_time: float):
        # Try to hit some notes
        self.hits += self._try_hit_note(current_time)
        # TODO: Miss notes, calc accuracy, apply HP
