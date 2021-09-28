from functools import total_ordering


# I'm calling it ChartNote because I don't want to put display stuff in this.
# DO NOT PUT DISPLAY STUFF IN THIS.
# I'll figure out display stuff later but God I keep mixing these two things
# and it trips me up every time.

class Flags:
    normal = "normal"


@total_ordering
class ChartNote:
    def __init__(self, pos: float, lane: int, length: float):  # I think every time should be in ms and sure
        self.pos = pos                                         # I guess we'll use floats since precision
        self.lane = lane                                       # isn't *that* important right?
        self.length = length
        self.flag = Flags.normal  # currently unused

        self.hit = False
        self.missed = False

    def hittable(self, current_time: float, window: tuple[float, float]):
        offset = current_time - self.pos

        # window is a tuple of the amount early you can be and the amount late you can be
        window_front_end, window_back_end = window
        window_front_end = -window_front_end

        return (not self.hit) and (not self.missed) and (window_front_end < offset < window_back_end)

    @property
    def lane_name(self):
        return ["left", "down", "up", "right"][self.lane]

    def __lt__(self, other):
        self.pos < other.pos


# This is for stuff in charts that's not notes
# This probably is a bad idea but I don't want to think of every type of event rn
class ChartEvent:
    def __init__(self, pos: float, name: str, **data):  # The **data thing means I don't need to make like
        self.pos = pos                                  # a hundred subclasses
        self.name = name
        self.data = data


class Chart:
    def __init__(self, name: str, diff: int, player: int, bpm: float, notespeed: float, notes: list[ChartNote], events: list[ChartEvent]):
        self.name = name
        self.diff = diff
        self.player = player
        self.bpm = bpm
        self.notespeed = notespeed
        self.notes = sorted(notes)
        self.events = sorted(events)

    # Might be helpful?
    @property
    def notes_and_events(self):
        return sorted(self.notes + self.events)     # sorted() is slow, calling it on a property is a bad idea

    @classmethod
    def from_JSON(jsondata: dict):
        song = jsondata["song"]
        name = song["song"]
        bpm = song["bpm"]
        notespeed = song["speed"]
        notes: list[ChartNote] = []
        for section in song["notes"]:
            if section["sectionNotes"]:
                for note in section:
                    notes.append(ChartNote(*note))  # expansions ahoy
        # diff is hardcoded right now because I don't know how to extract it from
        # the chart. I think it's just based on the name.
        # I'm also ignoring events for now since they don't technically exist in
        # charts and I'm going to be generating them.
        return Chart(name = name, diff = 2, bpm = bpm, notespeed = notespeed, notes = notes, events = [])
