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
        return None

    def set_target(self, lang, phrase: LanguagePhrase):
        self.targets[lang] = phrase

    def split(self, words: List[Word], split_at: int) -> 'Phrase':
        next = Phrase(
            id=-1,
            source=SourceLanguagePhrase(
                lang=self.source.lang,
                text=' '.join([w.word for w in words[split_at+1:self.source.end_word+1]]),
                start_time=words[split_at+1].start_time,
                end_time=words[self.end_word].end_time,
                start_word=split_at+1,
                end_word=self.source.end_word
            )
        )
        self.source.text = ' '.join([w.word for w in words[self.start_word:split_at + 1]])
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

    def to_srt(self, lang: str = None, include_source: bool = False) -> str:
        if lang is None:
            return self.source.to_srt(self.source)
        else:
            return self.get_target(lang).to_srt(source=self.source, include_source=include_source)

    def to_ass(self, style_name: str, lang: str = None, include_source: bool = False) -> str:
        if lang is None:
            return self.source.to_ass(source=self.source, style_name=style_name)
        else:
            return self.get_target(lang).to_ass(
                source=self.source,
                style_name=style_name,
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
