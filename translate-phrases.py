#!/usr/bin/env python3

import json
import fire
from typing import List
from functions import Phrase
import dotenv

dotenv.load_dotenv()


def cmd(phrases_file: str):
    with open(phrases_file, 'r') as f:
        phrases = []  # type: List[Phrase]
        for phrase in json.load(f):
            phrases.append(Phrase(**phrase))

    for phrase in phrases:
        phrase.translate_text('ar', 'en')

    print(Phrase.schema().dumps(phrases, many=True, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
