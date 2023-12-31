from .languagephrase import LanguagePhrase
from .phrasetiming import PhraseTiming
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
from .timings import Timings
from .word import Word
from . import strip_text


# @dataclass_json
@dataclass
class SourceLanguagePhrase(LanguagePhrase):

    reason: Optional[str] = None
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

        if start > end:
            # self.start_word = None
            # self.end_word = None
            self.timings.remove(Timings.SOURCE)
        else:
            # update source timings for phrase
            src_timing = PhraseTiming(
                start_time=words[start].start_time,
                end_time=words[end].end_time
            )
            self.timings.set(src_timing, Timings.SOURCE)

    def is_empty(self) -> bool:
        return self.start_word is None or self.end_word is None

    def is_equal(self, text: str) -> bool:
        return strip_text(self.text) == strip_text(text)
