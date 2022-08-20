from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from .word import Word
from .phrase import Phrase
import json


@dataclass_json
@dataclass
class Transcript:
    phrases: list[Phrase]
    src_lang: str
    words: list[Word] = field(default_factory=list)

    def to_srt(self, lang: str) -> str:
        srt = ''
        index = 1
        for phrase in self.phrases:
            srt += phrase.to_srt(lang)
            srt += "\n\n"
            index += 1

        return srt

    def save_audio(self, output_path, overwrite: bool = False, use_duration: bool = True):
        for target in self.targets.items():
            target.save_audio(
                output_path=output_path,
                overwrite=overwrite,
                use_duration=use_duration,
            )

    @classmethod
    def load_file(cls, file_name):
        with open(file_name, 'r') as f:
            data = json.load(f)
            return cls.from_dict(data)
