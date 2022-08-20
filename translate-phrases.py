#!/usr/bin/env python3

import json
import fire
from typing import List
from classes import *
import dotenv

dotenv.load_dotenv()


def cmd(phrases_file: str):
    container = PhrasesContainer.load_file(phrases_file)
    for phrase in container.phrases:
        phrase.translate_text('ar', 'en')

    print(Phrase.schema().dumps(container, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
