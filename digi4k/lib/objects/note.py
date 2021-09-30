from functools import total_ordering


# I'm calling it ChartNote because I don't want to put display stuff in this.
# DO NOT PUT DISPLAY STUFF IN THIS.
# I'll figure out display stuff later but God I keep mixing these two things
# and it trips me up every time.

class Flags:
    normal = "normal"


arrowmap = ["⬅", "⬇", "⬆", "➡"]


@total_ordering
class ChartNote:
    def __init__(self, pos: float, lane: int, length: float):  # I think every time should be in ms and sure
        self.pos = pos                                         # I guess we'll use floats since precision
        self.lane = lane                                       # isn't *that* important right?
        self.length = length
        self.flag = Flags.normal  # currently unused

        self.hit = False
        self.missed = False

    @property
    def pos_secs(self):
        return self.pos / 1000

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

    def __repr__(self):
        return f"<Note {self.pos}, {self.lane}, {self.length}, {self.flag}>"

    def __str__(self):
        flag = "" if self.flag == "normal" else self.flag.title() + " "
        arrow = arrowmap[self.lane]
        pos = f" P {round(self.position, 4)}"
        length = "" if self.length == 0 else f" L {round(self.length, 4)}"
        hit = " HIT" if self.hit else ""
        missed = " MISSED" if self.missed else ""
        return f"<Note {flag}{arrow}{pos}{length}{hit}{missed}>"


# This is for stuff in charts that's not notes
# This probably is a bad idea but I don't want to think of every type of event rn
class ChartEvent:
    def __init__(self, pos: float, name: str, **data):  # The **data thing means I don't need to make like
        self.pos = pos                                  # a hundred subclasses
        self.name = name
        self.data = data


class Chart:
    def __init__(self,  player: int, notespeed: float, notes: list[ChartNote], events: list[ChartEvent]):
        self.player = player
        self.notespeed = notespeed
        self.notes = sorted(notes)
        self.events = sorted(events)


class Song:
    def __init__(self, name: str, diff: int, bpm: float, charts: list[Chart], events: list[ChartEvent]):
        self.name = name
        self.diff = diff
        self.bpm = bpm
        self.charts = charts
        self.events = events

    # Might be helpful?
    @property
    def notes_and_events(self):
        return sorted(self.notes + self.events)     # sorted() is slow, calling it on a property is a bad idea

    @classmethod
    def from_json(cls, j: dict):
        song = j["song"]
        name = song["song"]
        bpm = song["bpm"]
        notespeed = song["speed"]
        p1notes: list[ChartNote] = []
        p2notes: list[ChartNote] = []
        songevents: list[ChartEvent] = []
        p1events: list[ChartEvent] = []
        p2events: list[ChartEvent] = []
        sections = song["notes"]
        lastMHS = None
        for section in sections:

            # Create a camera focus event like they should have in the first place
            mustHitSection: bool = section["mustHitSection"]
            if mustHitSection != lastMHS:
                if mustHitSection is True:  # fuck how do I get the current pos here
                    songevents.append(ChartEvent(..., "camera_focus", focus = "player1"))
                else:
                    songevents.append(ChartEvent(..., "camera_focus", focus = "player2"))

            # Actually make two charts
            sectionNotes: list = section["sectionNotes"]
            if sectionNotes:
                for note in sectionNotes:
                    low = (0, 1, 2, 3)  # wow look at the hardcoding~!
                    high = (4, 5, 6, 7)
                    pos, lane, length = note  # hope this never breaks lol
                    if mustHitSection:
                        if lane in low:
                            p1notes.append(ChartNote(pos, lane, length))
                        elif lane in high:
                            p2notes.append(ChartNote(pos, lane - 4, length))
                    else:
                        if lane in high:
                            p1notes.append(ChartNote(pos, lane - 4, length))
                        elif lane in low:
                            p2notes.append(ChartNote(pos, lane, length))
        # diff is hardcoded right now because I don't know how to extract it from
        # the chart. I think it's just based on the name.
        return Song(name = name, diff = 2, bpm = bpm, charts = [
            Chart(1, notespeed, p1notes, p1events),
            Chart(2, notespeed, p2notes, p2events)
        ], events = songevents)
