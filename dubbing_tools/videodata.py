import json
import os
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from .stilldata import StillData

__all__ = ['VideoData']

DATA_FILENAME = 'still-frames.json'


@dataclass_json
@dataclass
class VideoData:
    video_file: str
    stills: list[StillData] = field(default_factory=list)

    # write new entry in the json file
    def write(self, path: str):
        with open(os.path.join(path, DATA_FILENAME), 'w') as file:
            file.write(self.to_json(indent=2, ensure_ascii=False))

    @classmethod
    def read(cls, path: str) -> 'VideoData':
        with open(os.path.join(path, DATA_FILENAME), 'r') as file:
            data = json.load(file)
            return cls.from_dict(data)

    @property
    def last_still(self) -> StillData:
        return self.stills[-1]
