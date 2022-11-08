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

    def powerpoint_image_file(self) -> Optional[str]:
        m = re.search(r'-(?P<num>\d+)', self.image_file)
        if m:
            return f'Slide{int(m.group("num"))}.JPG'

        return None

    def duration(self) -> float:
        return self.time_start - self.time_end
