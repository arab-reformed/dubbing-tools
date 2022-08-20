from google.cloud import translate_v2 as translate
from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import re
import sys


def jsonify(result):
    if type(result) == list:
        return result

    json = []
    for i, section in enumerate(result['results']):
        section_alt = section['alternatives'][0]
        if 'transcript' in section_alt:
            import pprint
            # print(i)
            # pprint.pprint(section_alt)
            data = {
                "transcript": section_alt['transcript'],
                "end_time": section['resultEndTime'],
                "words": []
            }
            for word in section_alt['words']:
                data["words"].append({
                    "word": word['word'],
                    "start_time": word['startTime'],
                    "end_time": word['endTime'],
                    # "speaker_tag": word.speaker_tag
                })
            json.append(data)

    return json


def textify(transcript):
    txt = ''
    for section in transcript:
        section_text = ''
        for word in section['words']:
            section_text += (' ` ' if section_text else '') + word['word']

        txt += f"{section_text}\n\n"

    return txt


@dataclass_json
@dataclass
class Word:
    word: str
    start_time: float
    end_time: float
    hard_break: bool = False

    def __post_init__(self):
        self.set_word(self.word)

    def set_word(self, word: str):
        if '^' in word:
            self.hard_break = True
            word = word.replace('^', '')
        self.word = word.strip()

    def duration(self) -> float:
        return round(self.end_time - self.start_time, 2)

    def gap_between(self, next_word: 'Word'):
        return round(next_word.start_time - self.end_time, 2)

    def break_reason(self, next_word: 'Word', gap: float = 0.5) -> Optional[str]:
        if self.hard_break:
            return "^"

        # if self.gap_between(next_word) > 0.0:
            # print(f"  {self.gap_between(next_word)}", file=sys.stderr)

        if self.gap_between(next_word) > gap:
            return f"gap>{gap}"

        matches = re.search(r'(?P<punc>[.!?,])"*$', self.word)
        if matches:
            return matches.group('punc')

        return None

    def break_after(self, next_word: 'Word', gap: float = 0.5) -> bool:
        return self.break_reason(next_word=next_word, gap=gap) is not None

    @staticmethod
    def secs_to_float(secs: str):
        return round(float(secs.replace('s', '')), 2)


@dataclass_json
@dataclass
class Phrase:
    src_lang: str
    start_time: float
    end_time: float
    start_word: int
    end_word: int
    target_lang: str = None
    reason: str = None

    SRC_LANG = 1
    TARGET_LANG = 2

    def word_count(self) -> int:
        return self.end_word - self.start_word + 1

    def duration(self) -> float:
        return round(self.end_time - self.start_time, 2)

    def split(self, words: List[Word], split_at: int) -> 'Phrase':
        next = Phrase(
            src_lang=' '.join([w.word for w in words[split_at+1:self.end_word+1]]),
            start_time=words[split_at+1].start_time,
            end_time=words[self.end_word].end_time,
            start_word=split_at+1,
            end_word=self.end_word
        )
        self.src_lang = ' '.join([w.word for w in words[self.start_word:split_at+1]])
        self.end_time = words[split_at].end_time
        self.end_word = split_at

        return next

    @classmethod
    def words_to_phrase(cls, words: List[Word], start_word: int):
        return Phrase(
            src_lang=' '. join([w.word for w in words]),
            start_time=words[0].start_time,
            end_time=words[-1].end_time,
            start_word=start_word,
            end_word=start_word+len(words)-1
        )

    def translate_text(self, target_lang, source_lang=None):
        translate_client = translate.Client()
        result = translate_client.translate(
            self.src_lang,
            format_='text',
            target_language=target_lang,
            source_language=source_lang
        )

        self.target_lang = result['translatedText']

    def to_srt(self, lang: int, index) -> str:
        def _srt_time(seconds):
            millisecs = seconds * 1000
            seconds, millisecs = divmod(millisecs, 1000)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            return "%d:%d:%d,%d" % (hours, minutes, seconds, millisecs)
        if lang == self.SRC_LANG:
            text = self.src_lang
        else:
            text = self.target_lang

        return f"{index}\n" + _srt_time(self.start_time) + " --> " + _srt_time(self.end_time) + f"\n{text}"


@dataclass_json
@dataclass
class Phrases:
    src_lang: str
    target_lang: str
    phrases: List[Phrase] = None

    def __post_init__(self):
        if self.phrases is None:
            self.phrases = []

    def translate(self):
        for phrase in self.phrases:
            phrase.translate_text(self.target_lang, self.src_lang)

    def target_to_srt(self) -> str:
        srt = ''
        index = 1
        for phrase in self.phrases:
            srt += phrase.target_to_srt(index)
            srt += "\n\n"
            index += 1

        return srt

    def to_srt(self, lang: int) -> str:
        srt = ''
        index = 1
        for phrase in self.phrases:
            srt += phrase.to_srt(lang, index)
            srt += "\n\n"
            index += 1

        return srt


def get_phrases(words: List[Word], lang: str, gap: float = 1.0):
    clauses = [
        ['through', 'that', 'which', 'whereby', 'is'],
        ['of', 'by', 'about', 'from', 'in', 'into', 'for']
    ]

    phrases = []
    phrase = None
    reason = None
    for i, word in enumerate(words):
        if not phrase:
            phrase = Phrase(
                src_lang=word.word,
                start_time=word.start_time,
                end_time=word.end_time,
                start_word=i,
                end_word=i,
                reason=reason
            )

        else:
            phrase.src_lang += ' ' + word.word
            phrase.end_time = word.end_time
            phrase.end_word = i

        if i < len(words)-1:
            reason = word.break_reason(next_word=words[i+1], gap=gap)
        else:
            reason = None

        # If there's greater than one second gap, assume this is a new sentence
        if reason is not None:
            phrases.append(phrase)
            phrase = None

    if phrase:
        phrases.append(phrase)

    # Process phrases to make sure none are too long
    for small_gap in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
        changed = True
        while changed:
            changed = False
            shortened = []
            print(f"gap = {small_gap}", file=sys.stderr)
            for p, phrase in enumerate(phrases):
                shortened.append(phrase)
                print(f"Phrase: {p}", file=sys.stderr)
                if phrase.word_count() > 6:
                    for i in range(phrase.start_word+3, phrase.end_word-3):
                        reason = words[i].break_reason(next_word=words[i+1], gap=small_gap)
                        # print(i, reason, file=sys.stderr)
                        if reason is not None:
                            new = phrase.split(words, split_at=i)
                            new.reason = reason
                            shortened.append(new)
                            changed = True
                            break

            phrases = shortened

    for intros in clauses:
        changed = True
        while changed:
            changed = False
            shortened = []
            for phrase in phrases:
                shortened.append(phrase)
                if phrase.word_count() > 6:
                    for i in range(phrase.start_word+3, phrase.end_word-3):
                        if words[i].word in intros:
                            new = phrase.split(words, split_at=i-1)
                            new.reason = words[i].word
                            shortened.append(new)
                            changed = True
                            break

            phrases = shortened

    return phrases
