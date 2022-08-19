#!/usr/bin/env python3

import json
import fire
from functions import get_phrases, Word, Phrase


def cmd(words_file: str):
    with open(words_file, 'r') as f:
        words = []
        for word in json.load(f):
            words.append(Word(**word))

    phrases = get_phrases(words, 'en')

    print(Phrase.schema().dumps(phrases, many=True, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
