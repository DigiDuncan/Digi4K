from functools import total_ordering
from typing import Optional


# I'm calling it ChartNote because I don't want to put display stuff in this.
# DO NOT PUT DISPLAY STUFF IN THIS.
# I'll figure out display stuff later but God I keep mixing these two things
# and it trips me up every time.

class Flags:
    normal = "normal"
    fake = "fake"


arrowmap = ["⬅", "⬇", "⬆", "➡"]


@total_ordering
class ChartNote:
    def __init__(self, pos: float, lane: int, length: float):  # pos is in seconds
        self.pos = pos                                         # float percision is fine
        self.lane = lane                                       # don't worry about it
        self.length = length
        self.flag = Flags.normal  # currently unused

        self.hit = False
        self.hit_time = None
        self.missed = False

    def hittable(self, current_time: float, window_ms: tuple[float, float]) -> bool:
        # window is passed in in ms because everyone thinks of windows in ms
        window = window_ms[0] / 1000, window_ms[1] / 1000

        offset = current_time - self.pos

        # window is a tuple of the amount early you can be and the amount late you can be
        window_front_end, window_back_end = window
        window_front_end = -window_front_end

        return (not self.hit) and (not self.missed) and (window_front_end < offset < window_back_end)

    @property
    def lane_name(self) -> str:
        return ["left", "down", "up", "right"][self.lane]

    @property
    def hit_offset(self) -> Optional[float]:
        if self.hit_time is not None:
            return self.hit_time - self.pos
        return None

    @property
    def end(self) -> float:
        return self.pos + self.length

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
@total_ordering
class ChartEvent:
    def __init__(self, pos: float, name: str, **data):  # The **data thing means I don't need to make like
        self.pos = pos                                  # a hundred subclasses
        self.name = name
        self.data = data

    def __lt__(self, other):
        self.pos < other.pos


class Chart:
    def __init__(self,  player: int, notespeed: float, notes: list[ChartNote], events: list[ChartEvent]):
        self.player = player
        self.notespeed = notespeed
        self.notes: list[ChartNote] = sorted(notes)
        self.events: list[ChartEvent] = sorted(events)


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
        sections: list[dict] = song["notes"]
        lastBPM = bpm
        lastMHS = None
        notes_yet = False
        timesofar: float = 0
        for section in sections:
            # Since in theory you can have events in these sections
            # without there being notes there, I need to calculate where this
            # section occurs from scratch, and some engines have a startTime
            # thing here but I can't guarantee it so it's basically pointless
            seconds_per_beat = 60 / lastBPM
            seconds_per_measure = seconds_per_beat * 4
            seconds_per_sixteenth = seconds_per_measure / 16
            time_this_section = section["lengthInSteps"] * seconds_per_sixteenth

            # There's a changeBPM event but like, it always has to be paired
            # with a bpm, so it's pointless anyway
            newbpm = section.get("bpm", None)
            if newbpm is not None and newbpm != lastBPM:
                songevents.append(ChartEvent(timesofar, "change_bpm", bpm = newbpm))

            # Create a camera focus event like they should have in the first place
            mustHitSection: bool = section["mustHitSection"]
            if mustHitSection != lastMHS:
                if mustHitSection is True:
                    songevents.append(ChartEvent(timesofar, "camera_focus", focus = "player1"))
                else:
                    songevents.append(ChartEvent(timesofar, "camera_focus", focus = "player2"))
                lastMHS = mustHitSection

            sectionNotes: list = section["sectionNotes"]

            # 3, 2, 1, Go!
            if sectionNotes:
                if notes_yet is False:
                    notes_yet = True
                    messages = ["3", "2", "1", "go"]
                    for i in range(0, 16, 4):
                        songevents.append(ChartEvent(timesofar - seconds_per_measure + (seconds_per_sixteenth * i), "announcer", message = messages.pop(0)))

            # Actually make two charts
            if sectionNotes:
                for note in sectionNotes:
                    low = (0, 1, 2, 3)  # wow look at the hardcoding~!
                    high = (4, 5, 6, 7)
                    pos, lane, length = note  # hope this never breaks lol
                    pos /= 1000
                    length /= 1000
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

            # Increment current time
            timesofar += time_this_section

        # diff is hardcoded right now because I don't know how to extract it from
        # the chart. I think it's just based on the name.
        return Song(name = name, diff = 2, bpm = bpm, charts = [
            Chart(1, notespeed, p1notes, p1events),
            Chart(2, notespeed, p2notes, p2events)
        ], events = songevents)
