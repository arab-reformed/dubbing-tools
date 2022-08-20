from google.cloud import translate_v2 as translate
from typing import List, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from .phrase import OldPhrase
import json


@dataclass_json
@dataclass
class PhrasesContainer:
    src_lang: str
    target_lang: str
    phrases: List[OldPhrase] = field(default_factory=list)

    # def __post_init__(self):
    #     if self.phrases is None:
    #         self.phrases = []

    def phrase_count(self):
        return len(self.phrases)

    def translate(self):
        for phrase in self.phrases:
            phrase.translate_text(self.target_lang, self.src_lang)

    def to_srt(self, lang: str) -> str:
        srt = ''
        index = 1
        for phrase in self.phrases:
            srt += phrase.to_srt(lang)
            srt += "\n\n"
            index += 1

        return srt

    def save_audio(self, output_path: str, lang: str, overwrite: bool = False, use_duration: bool = True):
        for phrase in self.phrases:
            phrase.save_audio(
                output_path=output_path,
                lang=lang,
                use_duration=use_duration,
                overwrite=overwrite,
            )

    @classmethod
    def load_file(cls, file_name):
        with open(file_name, 'r') as f:
            data = json.load(f)
            phrases = []  # type: List[OldPhrase]
            for i, phrase in enumerate(data['phrases']):
                if 'id' not in phrase:
                    phrase['id'] = i
                phrases.append(OldPhrase(**phrase))

        return PhrasesContainer(
            phrases=phrases,
            src_lang=data['src_lang'],
            target_lang=data['target_lang']
        )
