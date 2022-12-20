from .languagephrase import LanguagePhrase
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
from .timings import Timings
from .word import Word


# @dataclass_json
@dataclass
class SourceLanguagePhrase(LanguagePhrase):

    reason: str = None
    start_word: int = None
    end_word: int = None

    # def __post_init__(self):
    #     if hasattr(self, 'start_time'):
    #         self.timings.default = Timings.SOURCE
    #     super().__post_init__()

    def word_count(self) -> Optional[int]:
        if self.start_word is not None and self.end_word is not None:
            return self.end_word - self.start_word + 1
        return None

    def set_by_word_indices(self, words: list[Word], start: int, end: int):
        super().set_by_word_indices(words, start, end)
        self.start_word = start
        self.end_word = end
