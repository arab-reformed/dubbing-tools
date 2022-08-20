#!/usr/bin/env python3

import json
import fire
from functions import get_phrases
from classes import *


def cmd(words_file: str):
    with open(words_file, 'r') as f:
        words = []
        for word in json.load(f):
            words.append(Word(**word))

    phrases = get_phrases(words, 'en')
    container = PhrasesContainer(
        phrases=phrases,
        src_lang='en',
        target_lang='ar',
    )

    print(container.to_json(indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
