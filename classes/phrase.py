from dataclasses import dataclass, field
from .languagephrase import LanguagePhrase
from google.cloud import translate_v2 as translate
from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .word import Word
from .sourcelanguagePhrase import SourceLanguagePhrase


@dataclass_json
@dataclass
class Phrase:
    id: int
    source: SourceLanguagePhrase
    targets:  dict[str, LanguagePhrase] = field(default_factory=dict)
    reason: str = None

    def __post_init__(self):
        self.set_id(self.id)

    def set_id(self, id: int):
        self.id = id
        self.source.id = self.id
        for lang in self.targets:
            self.get_target(lang).id = self.id

    def translate_text(self, target_lang):
        translate_client = translate.Client()
        result = translate_client.translate(
            self.source.text,
            format_='text',
            target_language=target_lang,
            source_language=self.source.lang
        )

        self.set_text(target_lang, result['translatedText'])

    def get_text(self, lang: str) -> Optional[str]:
        if lang in self.targets:
            return self.get_target(lang).text
        return None

    def set_text(self, lang, text):
        if lang in self.targets:
            self.get_target(lang).text = text
        else:
            self.set_target(lang, LanguagePhrase(lang=lang, text=text))

    def get_target(self, lang: str) -> Optional[LanguagePhrase]:
        if lang in self.targets:
            return self.targets[lang]

        elif lang == self.source.lang:
            return self.source

        return None

    def set_target(self, lang, phrase: LanguagePhrase):
        self.targets[lang] = phrase
        phrase.id = self.id

    def split(self, words: List[Word], split_at: int) -> 'Phrase':
        next = Phrase(
            id=-1,
            source=SourceLanguagePhrase(
                lang=self.source.lang,
                text=' '.join([w.word for w in words[split_at+1:self.source.end_word+1]]),
                start_time=words[split_at+1].start_time,
                end_time=words[self.source.end_word].end_time,
                start_word=split_at+1,
                end_word=self.source.end_word
            )
        )
        self.source.text = ' '.join([w.word for w in words[self.source.start_word:split_at + 1]])
        self.source.end_time = words[split_at].end_time
        self.source.end_word = split_at

        return next

    @classmethod
    def words_to_phrase(cls, lang: str, words: List[Word], start_word: int):
        return cls(
            id=-1,
            source=SourceLanguagePhrase(
                lang=lang,
                text=' '. join([w.word for w in words]),
                start_time=words[0].start_time,
                end_time=words[-1].end_time,
                start_word=start_word,
                end_word=start_word+len(words)-1
            )
        )

    def get_tts_audio_natural(self, lang: str, overwrite: bool = False):
        self.get_target(lang).get_tts_natural_audio(
            overwrite=overwrite
        )

    def get_tts_audio_duration(self, lang: str, overwrite: bool = False):
        self.get_target(lang).get_tts_duration_audio(
            overwrite=overwrite
        )

    def to_srt(self, lang: str, timings_lang: str = None, include_source: bool = False) -> str:
        timings = None
        if timings_lang is not None:
            timings = self.get_target(timings_lang)

        return self.get_target(lang).to_srt(
            source=self.source,
            timings=timings,
            include_source=include_source
        )

    def to_ass(self, lang: str, timings_lang: str = None, include_source: bool = False) -> str:
        timings = None
        if timings_lang is not None:
            timings = self.get_target(timings_lang)

        return self.get_target(lang).to_ass(
            source=self.source,
            timings=timings,
            include_source=include_source
        )

    def to_csv(self, lang: str) -> tuple:
        return (
            self.id,
            self.source.start_time,
            self.source.end_time,
            self.source.text,
            self.get_target(lang).text,
        )
