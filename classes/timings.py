from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional
from .phrasetiming import PhraseTiming


@dataclass_json
@dataclass
class Timings:
    TIMING_SOURCE = 'src'
    TIMING_DUBBED = 'dub'
    TIMING_TRANSLATION = 'trn'
    TIMING_SCHEMES = {
        TIMING_SOURCE: 'timing',
        TIMING_DUBBED: 'dubbed',
        TIMING_TRANSLATION: 'translation',
    }

    default: str = TIMING_DUBBED

    phrase_timings: dict[str, PhraseTiming] = field(default_factory=dict)

    def get(self, scheme: str = None) -> Optional[PhraseTiming]:
        if scheme is None:
            scheme = self.default

        if scheme in self.TIMING_SCHEMES and scheme in self.phrase_timings:
            return self.phrase_timings[scheme]

        return None

    def set(self, timing: PhraseTiming, scheme: str = None) -> None:
        if scheme is None:
            scheme = self.default

        self.phrase_timings[scheme] = timing
