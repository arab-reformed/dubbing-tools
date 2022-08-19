from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json


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
        return round(self.end_time - next_word.start_time, 2)

    def break_after(self, next_word: 'Word'):
        return self.hard_break or self.gap_between(next_word) > 0.5

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

    def word_count(self) -> int:
        return self.end_word - self.start_word + 1

    def duration(self) -> float:
        return round(self.end_time - self.start_time, 2)

    def split(self, words: List[Word], split_at: int) -> 'Phrase':
        next = Phrase(
            src_lang=' '.join([w.word for w in words[split_at+1:self.end_word]]),
            start_time=words[split_at+1].start_time,
            end_time=words[self.end_word].end_time,
            start_word=split_at+1,
            end_word=self.end_word,
        )
        self.src_lang = ' '.join([w.word for w in words[self.start_word:split_at]])
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


def get_phrases(words: List[Word], lang: str, gap: float = 1.0):

    phrases = []
    phrase = None
    for i, word in enumerate(words):
        if not phrase:
            phrase = Phrase(
                src_lang=word.word,
                start_time=word.start_time,
                end_time=word.end_time,
                start_word=i,
                end_word=i,
            )
        else:
            phrase.src_lang += ' ' + word.word
            phrase.end_time = word.end_time
            phrase.end_word = i

        # If there's greater than one second gap, assume this is a new sentence
        if word.word[-1] in [',', '.', '?', '!'] or \
                i < len(words)-1 and word.end_time - words[i + 1].start_time > gap:
            phrases.append(phrase)
            phrase = None

    if phrase:
        phrases.append(phrase)

    # Process phrases to make sure none are too long
    shortened = []
    for phrase in phrases:
        shortened.append(phrase)
        if phrase.word_count() > 6:
            for i in range(phrase.start_word+2, phrase.end_word-3):
                if words[i].break_after(words[i+1]):
                    shortened.append(phrase.split(words, i))

    return phrases
