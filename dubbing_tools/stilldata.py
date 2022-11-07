from dataclasses import dataclass, field
from dataclasses_json import dataclass_json

__all__ = ['StillData']


@dataclass_json
@dataclass
class StillData:
    frame_start: int
    frame_end: int
    time_start: float
    time_end: float
    image_file: str = None
