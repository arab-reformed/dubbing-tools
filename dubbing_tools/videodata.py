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

    def write(self, output_path: str):
        with open(os.path.join(output_path, DATA_FILENAME), 'w') as file:
            file.write(self.to_json(indent=2, ensure_ascii=False))

    @classmethod
    def read(cls, output_path: str):
        with open(os.path.join(output_path, DATA_FILENAME), 'r') as file:
            data = json.load(file)
            return cls.from_dict(data)

    @property
    def last_still(self):
        return self.stills[-1]
