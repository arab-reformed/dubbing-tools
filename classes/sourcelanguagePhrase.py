from .languagephrase import LanguagePhrase
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
from .timings import Timings


@dataclass_json
@dataclass
class SourceLanguagePhrase(LanguagePhrase):

    reason: str = None
    start_word: int = None
    end_word: int = None

    def __post_init__(self):
        if hasattr(self, 'start_time'):
            self.timings.default = Timings.SOURCE
        super().__post_init__()

    def word_count(self) -> Optional[int]:
        if self.start_word is not None and self.end_word is not None:
            return self.end_word - self.start_word + 1
        return None
