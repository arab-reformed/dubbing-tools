from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional
from .phrasetiming import PhraseTiming


@dataclass_json
@dataclass
class Timings:
    SOURCE = 'src'
    DUBBED = 'dub'
    TRANSLATION = 'trn'
    SCHEMES = {
        SOURCE: 'timing',
        DUBBED: 'dubbed',
        TRANSLATION: 'translation',
    }

    default: str = DUBBED

    phrase_timings: dict[str, PhraseTiming] = field(default_factory=dict)

    def get(self, scheme: str = None) -> Optional[PhraseTiming]:
        if scheme is None:
            scheme = self.default

        if scheme in self.SCHEMES and scheme in self.phrase_timings:
            return self.phrase_timings[scheme]

        return None

    def set(self, timing: PhraseTiming, scheme: str = None) -> None:
        if scheme is None:
            scheme = self.default

        self.phrase_timings[scheme] = timing

    def schemes(self):
        return list(self.phrase_timings.keys())
