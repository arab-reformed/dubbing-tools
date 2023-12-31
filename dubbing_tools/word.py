from . import strip_text
from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import re


@dataclass_json
@dataclass
class Word:
    id: int
    word: str
    start_time: float
    end_time: float
    hard_break: bool = False
    manuscript_break_before: bool = False
    comment: Optional[str] = None

    def __post_init__(self):
        self.set_word(self.word)

    def set_word(self, word: str):
        if '^' in word:
            self.hard_break = True
            word = word.replace('^', '')
        self.word = word.strip()

    def duration(self) -> float:
        return round(self.end_time - self.start_time, 3)

    def gap_between(self, next_word: 'Word') -> float:
        return round(next_word.start_time - self.end_time, 3)

    def break_reason(self, next_word: 'Word', gap: float = 0.5) -> Optional[str]:
        if self.hard_break:
            return "^"

        # if self.gap_between(next_word) > 0.0:
        import sys
        # print(f"  {self.gap_between(next_word)}", file=sys.stderr)
        # print(type(self.gap_between(next_word)))
        # print(type(gap))
        if next_word.manuscript_break_before:
            return 'manuscript_break'

        elif self.gap_between(next_word) > gap:
            return f"gap>{gap}"

        elif (matches := re.search(r'^(?P<word>.*?)(?P<punc>[.!?,])"*$', self.word)) and matches.group('word') != next_word.word:
            return matches.group('punc')

        return None

    def break_after(self, next_word: 'Word', gap: float = 0.5) -> bool:
        return self.break_reason(next_word=next_word, gap=gap) is not None

    @staticmethod
    def secs_to_float(secs: str):
        return round(float(secs.replace('s', '')), 3)

    def is_equal(self, text: str) -> bool:
        return strip_text(self.word) == strip_text(text)
