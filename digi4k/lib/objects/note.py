from __future__ import annotations

from typing import Any, Iterable, Optional, TypedDict, Literal, Union
from functools import total_ordering

from digi4k.lib.utils import EnumPlus

# typing
PlayerNum = Literal[1, 2]
LaneNum = Literal[0, 1, 2, 3]
LANES: list[LaneNum] = [0, 1, 2, 3]
JsonLaneNum = Literal[0, 1, 2, 3, 4, 5, 6, 7]
Seconds = float
Milliseconds = float

Difficulty = Literal[1, 2, 3]


class Difficulties(metaclass=EnumPlus):     # noqa: E302
    EASY = 1
    NORMAL = 2
    HARD = 3


class SongFileJson(TypedDict):
    song: SongJson


class SongJson(TypedDict):
    song: str
    bpm: float
    speed: float
    notes: list[NoteJson]


class NoteJson(TypedDict):
    bpm: float
    mustHitSection: bool
    sectionNotes: list[tuple[Milliseconds, JsonLaneNum, Milliseconds]]
    lengthInSteps: int


Flag = Literal["normal", "bomb", "death", "gold", "fake", "strikeline"]


class Flags(metaclass=EnumPlus):    # noqa: E302
    NORMAL = "normal"
    BOMB = "bomb"
    DEATH = "death"
    GOLD = "gold"
    FAKE = "fake"
    STRIKELINE = "strikeline"

# end of typing


# I'm calling it ChartNote because I don't want to put display stuff in this.
# DO NOT PUT DISPLAY STUFF IN THIS.
# I'll figure out display stuff later but God I keep mixing these two things
# and it trips me up every time.


@total_ordering
class ChartEvent:
    def __init__(self, pos: Seconds):
        # pos is in seconds, float percision is fine, don't worry about it
        self.pos = pos
        self.icon = "missing"

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, ChartEvent):
            return NotImplemented
        return self.pos < other.pos

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ChartEvent)
            and self.pos == other.pos
        )

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} pos: {round(self.pos, 3)}>"


class ChartNote(ChartEvent):
    ARROWMAP = ["⬅", "⬇", "⬆", "➡"]

    def __init__(self, pos: Seconds, lane: LaneNum, length: Seconds, *, flag: Flag = Flags.NORMAL):
        super().__init__(pos)
        self.lane = lane
        self.length = length
        self.flag: Flag = flag

        self.hit = False
        self.missed = False
        self.hit_time: Optional[float] = None

    @property
    def hit_offset(self) -> Union[float, None]:
        if self.hit_time is None:
            return None
        return self.hit_time - self.pos

    @property
    def lane_name(self) -> str:
        return ["left", "down", "up", "right"][self.lane]

    def __lt__(self, other: Any) -> bool:
        # If the parent class determines they aren't equal, then return parent class's __lt__
        if not super().__eq__(other):
            return super().__lt__(other)

        # If the other is not a ChartNote, just group all the classes of the same name together
        if not isinstance(other, ChartNote):
            return self.__class__.__name__ < other.__class__.__name__

        # They are both ChartNotes at the same position
        return (self.lane, self.length, self.flag) < (other.lane, other.length, other.flag)

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ChartNote)
            and super().__eq__(other)
            and (self.lane, self.length, self.flag) == (other.lane, other.length, other.flag)
        )

    def __repr__(self) -> str:
        return f"<Note {self.pos}, {self.lane}, {self.length}, {self.flag}>"

    def __str__(self) -> str:
        flag = "" if self.flag == "normal" else self.flag.title() + " "
        arrow = self.ARROWMAP[self.lane]
        pos = f" P {round(self.pos, 4)}"
        length = "" if self.length == 0 else f" L {round(self.length, 4)}"
        hit = " HIT" if self.hit else ""
        missed = " MISSED" if self.missed else ""
        return f"<Note {flag}{arrow}{pos}{length}{hit}{missed}>"


class ChangeBpmEvent(ChartEvent):
    def __init__(self, pos: Seconds, bpm: float):
        super().__init__(pos)
        self.bpm = bpm
        self.icon = "bpm"

    def __lt__(self, other: Any) -> bool:
        # If the parent class determines they aren't equal, then return parent class's __lt__
        if not super().__eq__(other):
            return super().__lt__(other)

        # If the other is not a ChangeBpmEvent, just group all the classes of the same name together
        if not isinstance(other, ChangeBpmEvent):
            return self.__class__.__name__ < other.__class__.__name__

        # They are both ChartNotes at the same position
        return self.bpm < other.bpm

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, ChangeBpmEvent)
            and super().__eq__(other)
            and self.bpm == other.bpm
        )


class CameraFocusEvent(ChartEvent):
    def __init__(self, pos: Seconds, focused_player: PlayerNum):
        super().__init__(pos)
        self.focused_player = focused_player
        self.icon = f"cam_p{focused_player}"

    def __lt__(self, other: Any) -> bool:
        # If the parent class determines they aren't equal, then return parent class's __lt__
        if not super().__eq__(other):
            return super().__lt__(other)

        # If the other is not a CameraFocusEvent, just group all the classes of the same name together
        if not isinstance(other, CameraFocusEvent):
            return self.__class__.__name__ < other.__class__.__name__

        # They are both CameraFocusEvent at the same position
        return self.focused_player < other.focused_player

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, CameraFocusEvent)
            and super().__eq__(other)
            and self.focused_player == other.focused_player
        )


class AnnouncerEvent(ChartEvent):
    def __init__(self, pos: Seconds, message: str):
        super().__init__(pos)
        self.message = message
        self.icon = f"announcer_{message}"

    def __lt__(self, other: Any) -> bool:
        # If the parent class determines they aren't equal, then return parent class's __lt__
        if not super().__eq__(other):
            return super().__lt__(other)

        # If the other is not a AnnouncerEvent, just group all the classes of the same name together
        if not isinstance(other, AnnouncerEvent):
            return self.__class__.__name__ < other.__class__.__name__

        # They are both AnnouncerEvent at the same position
        return self.message < other.message

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, AnnouncerEvent)
            and super().__eq__(other)
            and self.message == other.message
        )


class Chart:
    def __init__(self,  player: PlayerNum, notespeed: float):
        self.player = player
        self.notespeed = notespeed
        self.notes: list[ChartNote] = []
        self.active_notes: list[ChartNote] = []
        self.events: list[ChartEvent] = []

    def get_hittable_notes(self, current_time: Seconds, front_end: Seconds, back_end: Seconds) -> Iterable[ChartNote]:
        n = 0
        while n < len(self.active_notes):
            note = self.active_notes[n]
            is_expired = note.pos < current_time - back_end
            is_waiting = note.pos > current_time + front_end
            if is_expired:
                del self.active_notes[n]
                n -= 1
            elif is_waiting:
                break
            else:
                yield note
            n += 1


class Song:
    def __init__(self, name: str, diff: Difficulty, bpm: float, charts: tuple[Chart, Chart], events: list[ChartEvent]):
        self.name = name
        self.diff = diff
        self.bpm = bpm
        self.charts = charts
        self.events = events

    @classmethod
    def from_json(cls, j: SongFileJson) -> Song:
        song = j["song"]
        name = song["song"]
        bpm = song["bpm"]
        notespeed = song["speed"]
        charts = Chart(1, notespeed), Chart(2, notespeed)
        charts_by_playernum = {c.player: c for c in charts}

        last_bpm = bpm
        last_focus: Optional[PlayerNum] = None
        section_start = 0.0
        songevents: list[ChartEvent] = []
        sections = song["notes"]
        section_starts = []
        for section in sections:
            # There's a changeBPM event but like, it always has to be paired
            # with a bpm, so it's pointless anyway
            if "bpm" in section:
                new_bpm = section["bpm"]
                if new_bpm != last_bpm:
                    songevents.append(ChangeBpmEvent(section_start, new_bpm))
                    last_bpm = new_bpm
            section_starts.append((section_start, bpm))

            # Create a camera focus event like they should have in the first place
            if section["mustHitSection"]:
                focused, unfocused = 1, 2
            else:
                focused, unfocused = 2, 1

            if focused != last_focus:
                songevents.append(CameraFocusEvent(section_start, focused))
                last_focus = focused

            # Actually make two charts
            sectionNotes = section["sectionNotes"]
            for note in sectionNotes:
                posms, lane, lengthms = note  # hope this never breaks lol
                pos = posms / 1000
                length = lengthms / 1000

                note_in_focused_lane = lane < 4
                note_player = focused if note_in_focused_lane else unfocused
                lanemap: list[LaneNum] = [0, 1, 2, 3, 0, 1, 2, 3]
                chart_lane: LaneNum = lanemap[lane]

                charts_by_playernum[note_player].notes.append(ChartNote(pos, chart_lane, length))

            # Since in theory you can have events in these sections
            # without there being notes there, I need to calculate where this
            # section occurs from scratch, and some engines have a startTime
            # thing here but I can't guarantee it so it's basically pointless
            seconds_per_beat = 60 / bpm
            seconds_per_measure = seconds_per_beat * 4
            seconds_per_sixteenth = seconds_per_measure / 16
            section_length = section["lengthInSteps"] * seconds_per_sixteenth
            section_start += section_length

        for c in charts:
            c.notes.sort()
            c.active_notes = c.notes.copy()
            c.events.sort()

        # 3, 2, 1, Go!
        if any(c.notes for c in charts):
            first_note = min(n for c in charts for n in c.notes[:1])
            announcer_end, bpm = next((ss, bpm) for ss, bpm in section_starts if first_note.pos <= ss)
            seconds_per_beat = 60 / bpm
            for i, m in ((4, "3"), (3, "2"), (2, "1"), (1, "go")):
                message_start = announcer_end - (seconds_per_beat * i)
                songevents.append(AnnouncerEvent(message_start, m))

        songevents.sort()

        # diff is hardcoded right now because I don't know how to extract it from
        # the chart. I think it's just based on the name.
        return Song(
            name,
            Difficulties.NORMAL,
            bpm,
            charts,
            songevents
        )
