from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
import re
from typing import Optional

__all__ = ['StillData']


@dataclass_json
@dataclass
class StillData:
    frame_start: int
    frame_end: int
    time_start: float
    time_end: float
    image_file: str = None

    def get_image_file(self, still, pp) -> Optional[str]:
        if pp:
            m = re.search(r'-(?P<num>\d+)', self.image_file)
            if m:
                return f'Slide{int(m.group("num"))}.JPG'
        else:
            return still.image_file

    def duration(self) -> float:
        return self.time_end - self.time_start
