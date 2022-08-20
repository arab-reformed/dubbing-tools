from .languagephrase import LanguagePhrase
from dataclasses import dataclass
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class SourceLanguagePhrase(LanguagePhrase):

    reason: str = None
    start_word: int = None
    end_word: int = None
