#!/usr/bin/env python3

import json
import fire
from typing import List
from classes import *
import dotenv

dotenv.load_dotenv()


def cmd(phrases_file: str, lang: str):
    container = PhrasesContainer.load_file(phrases_file)

    print(container.to_srt(lang=lang))


if __name__ == "__main__":
    fire.Fire(cmd)
