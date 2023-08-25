import sys
from dataclasses import dataclass, field
from google.cloud import translate_v2 as translate
from typing import List, Optional
from dataclasses_json import dataclass_json
from .languagephrase import LanguagePhrase
from .word import Word
from .sourcelanguagePhrase import SourceLanguagePhrase
from .timings import Timings
from .phrasetiming import PhraseTiming
from dubbing_tools import SUBTITLE_GAP


@dataclass_json
@dataclass
class Phrase:
    id: int
    source: SourceLanguagePhrase
    targets:  dict[str, LanguagePhrase] = field(default_factory=dict)
    reason: Optional[str] = None

    def __post_init__(self):
        try:
            self.set_children_id(self.id)
        except Exception as e:
            print(f"{e}")
            raise e

    # def __setattr__(self, key, value):
    #     if key == 'id':
    #         self.set_children_id(self.id)
    #
    #     super().__setattr__(key, value)

    def set_children_id(self, id: int):
        try:
            if self.source:
                self.source.id = self.id
            for lang in self.targets:
                self.get_target(lang).id = self.id
        except Exception as e:
            print(f"{e}")
            raise e

    def get_timing(self, lang: str, timing_scheme: str = None) -> PhraseTiming:
        return self.get_target(lang).timings.get(timing_scheme)

    def set_timing(self, lang: str, timing_scheme: str, timing: PhraseTiming):
        self.get_target(lang).timings.set(scheme=timing_scheme, timing=timing)

    def translate_text(self, target_lang):
        translate_client = translate.Client()
        result = translate_client.translate(
            self.source.text,
            format_='text',
            target_language=target_lang,
            source_language=self.source.lang
        )

        self.set_text(target_lang, result['translatedText'])
        print(f"{self.id}: {self.source.text} --> {result['translatedText']}")

    def get_text(self, lang: str) -> Optional[str]:
        if lang in self.targets:
            return self.get_target(lang).text
        return None

    def set_text(self, lang, text):
        target = self.get_target(lang)
        if target is not None:
            target.set_text(text)

        else:
            self.set_target(lang, LanguagePhrase(lang=lang, text=text))

    def get_target(self, lang: str) -> Optional[LanguagePhrase]:
        if lang in self.targets:
            return self.targets[lang]

        elif lang == self.source.lang:
            return self.source

        return None

    def set_target(self, lang: str, phrase: LanguagePhrase):
        self.targets[lang] = phrase
        phrase.id = self.id

    def delete_target(self, lang: str):
        del self.targets[lang]

    def split(self, words: List[Word], split_at: int) -> 'Phrase':
        next = Phrase(
            id=-1,
            source=SourceLanguagePhrase(
                lang=self.source.lang,
                text=' '.join([w.word for w in words[split_at+1:self.source.end_word+1]]),
                start_word=split_at+1,
                end_word=self.source.end_word
            )
        )
        next.source.timings.set(
            scheme=Timings.SOURCE,
            timing=PhraseTiming(
                start_time=words[split_at+1].start_time,
                end_time=words[self.source.end_word].end_time,
            )
        )
        self.source.text = ' '.join([w.word for w in words[self.source.start_word:split_at + 1]])
        self.source.timings.get(Timings.SOURCE).end_time = words[split_at].end_time
        self.source.end_word = split_at

        return next

    @classmethod
    def words_to_phrase(cls, lang: str, words: List[Word], start_word: int) -> 'Phrase':
        p = cls(
            id=-1,
            source=SourceLanguagePhrase(
                lang=lang,
                text=' '. join([w.word for w in words]),
                start_word=start_word,
                end_word=start_word+len(words)-1
            )
        )
        p.source.timings.set(
            scheme=Timings.SOURCE,
            timing=PhraseTiming(
                start_time=words[0].start_time,
                end_time=words[-1].end_time,
            )
        )
        return p

    def get_tts_audio_natural(self, lang: str, overwrite: bool = False):
        self.get_target(lang).get_tts_natural_audio(
            overwrite=overwrite
        )

    def get_tts_audio_duration(self, lang: str, timing_scheme: str, overwrite: bool = False):
        self.get_target(lang).get_tts_duration_audio(
            timing_scheme=timing_scheme,
            overwrite=overwrite
        )

    def to_srt(self, audio_lang: str, timings_lang: str = None, timing_scheme: str = None, include_source: bool = False) -> str:
        timings = None
        if timings_lang is not None:
            timings = self.get_target(timings_lang).timings.get(timing_scheme)

        return self.get_target(audio_lang).to_srt(
            source=self.source,
            timing=timings,
            include_source=include_source
        )

    def to_ass(self, prev_phrase: 'Phrase', next_phrase: 'Phrase', audio_lang: str, timing_scheme: str, subtitle_lang: str,
               include_source: bool = False, debug: bool = False) -> str:
        timing = self.get_timing(audio_lang, timing_scheme)
        target = self.get_target(subtitle_lang)
        count = len(target.text)
        start = timing.start_time
        if prev_phrase:
            prev_timing = prev_phrase.get_timing(audio_lang, timing_scheme)
            gap = start - prev_timing.end_time
            if gap > SUBTITLE_GAP:
                prev_count = len(prev_phrase.get_target(subtitle_lang).text)
                start -= (gap - SUBTITLE_GAP) * count / (prev_count + count)

        end = timing.end_time
        if next_phrase:
            next_timing = next_phrase.get_timing(audio_lang, timing_scheme)
            gap = next_timing.start_time - end
            if gap > SUBTITLE_GAP:
                next_count = len(next_phrase.get_target(subtitle_lang).text)
                end += (gap - SUBTITLE_GAP) * count / (count + next_count)

        return target.to_ass(
            start=start,
            end=end,
            source=self.source if include_source else None,
            debug=debug,
        )

    def to_csv(self, lang: str) -> tuple:
        timing = self.source.timings.get(Timings.SOURCE)
        return (
            self.id,
            timing.start_time,
            timing.end_time,
            self.source.text,
            self.get_target(lang).text if self.get_target(lang) else '',
        )
