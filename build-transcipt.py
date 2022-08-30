#!/usr/bin/env python3

import json
import os.path

import fire
from typing import List
from dubbing_tools import *
import dotenv

dotenv.load_dotenv()


def cmd(phrases_file: str, words_file: str):
    with open(phrases_file, 'r') as f:
        phrase_data = json.load(f)

    with open(words_file, 'r') as f:
        word_data = json.load(f)

    src_lang = phrase_data['src_lang'] if 'src_lang' in phrase_data else 'en'
    target_lang = phrase_data['target_lang'] if 'target_lang' in phrase_data else 'ar'

    phrases = []  # type: list[Phrase]
    for phrase in phrase_data['phrases'] if 'phrases' in phrase_data else phrase_data:
        p = Phrase(
            id=len(phrases)+1,
            reason=phrase['reason'],
            source=SourceLanguagePhrase(
                lang=src_lang,
                text=phrase['src_lang'],
                start_time=phrase['start_time'],
                end_time=phrase['end_time'],
                start_word=phrase['start_word'],
                end_word=phrase['end_word']
            )
        )
        p.set_text(target_lang, phrase['target_lang'])
        if 'target_duration' in phrase:
            p.get_target(target_lang).natural_duration = phrase['target_duration']

        if 'audio_file' in phrase:
            path = os.path.relpath(phrase['audio_file'])
            p.get_target(target_lang).audio_file = path

        phrases.append(p)

    words = []  # type: list[Word]
    for word in word_data:
        if 'id' not in word:
            word['id'] = len(words) + 1
        words.append(Word.from_dict(word))

    transcript = Transcript(
        src_lang=src_lang,
        phrases=phrases,
        words=words
    )

    print(transcript.to_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    fire.Fire(cmd)
