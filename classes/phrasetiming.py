from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional


@dataclass_json
@dataclass
class PhraseTiming:
    start_time: float = None
    end_time: float = None
    freeze_time: Optional[float] = None
    freeze_duration: Optional[float] = None

    def __setattr__(self, key, value):
        if key in ['start_time', 'end_time', 'freeze_time', 'freeze_duration']:
            value = self.rnd(value)

        super().__setattr__(key, value)

    def duration(self) -> float:
        return self.rnd(self.end_time - self.start_time)

    def gap_between(self, timing: 'Timings') -> float:
        if timing.start_time > self.start_time:
            return self.rnd(timing.start_time - self.end_time)

        return self.rnd(self.start_time - timing.end_time)

    def expand(self, at_speed: float) -> float:
        self.freeze_time = None
        self.freeze_duration = None
        if self.audio_speed() > at_speed:
            self.freeze_time = round(self.end_time, 3)
            self.freeze_duration = round(self.natural_audio.duration / at_speed - self.duration(), 3)
            self.end_time = round(self.end_time + self.freeze_duration, 3)
            return self.freeze_duration

        return 0.0

    def shift(self, increment: float) -> bool:
        # TODO: make sure not shifted past the end of the video
        if self.start_time - increment < 0:
            return False

        self.start_time += increment
        self.end_time += increment
        return True

    def move_start(self, increment: float) -> bool:
        if self.start_time - increment < 0:
            return False
        self.start_time += increment
        return True

    def move_end(self, increment: float) -> bool:
        # TODO: make sure not shifted past the end of the video
        self.end_time += increment
        return True

    def reset_timing(self, timing: 'PhraseTiming'):
        self.start_time = timing.start_time
        self.end_time = timing.end_time
        self.freeze_duration = None
        self.freeze_time = None

    @staticmethod
    def rnd(value: float) -> float:
        return round(value, 3)
