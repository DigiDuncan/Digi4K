from digi4k.lib.objects.note import Chart


class InputParser:
    def __init__(self, front_end, back_end):
        # Hardcoding these now sorry
        self.front_end = 166 * (2 / 3)
        self.back_end = 166 * (1 / 3)

    def try_hit_note(self, current_time: float, lanes: list[int], chart: Chart) -> bool:
        notes = chart.notes
        for lane in lanes:
            good_notes = sorted([note for note in notes if note.lane == lane and note.hittable(current_time, (self.front_end, self.back_end))])
            if good_notes:
                good_notes[0].hit = True
                return True
        return False
