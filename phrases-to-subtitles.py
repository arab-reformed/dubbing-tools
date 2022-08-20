#!/usr/bin/env python3

import json
import fire
from typing import List
from functions import Phrase, Project
import dotenv

dotenv.load_dotenv()


def cmd(phrases_file: str, lang: int):
    with open(phrases_file, 'r') as f:
        phrases = []  # type: List[Phrase]
        for phrase in json.load(f):
            phrases.append(Phrase(**phrase))

    project = Project(phrases=phrases, src_lang='en', target_lang='ar')

    print(project.to_srt(lang=lang))


if __name__ == "__main__":
    fire.Fire(cmd)
