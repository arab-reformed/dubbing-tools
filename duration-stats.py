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
        ratio = round(phrase.target_duration / phrase.duration(), 2)
        print(f"{str(phrase.id).rjust(3)}: {str(phrase.target_duration).rjust(5)} / {str(phrase.duration()).rjust(4)} = {str(ratio).rjust(5)}")
        if phrase.id < container.phrase_count()-1:
            print(f"   : {phrase.gap_between(container.phrases[phrase.id+1])}")


if __name__ == "__main__":
    fire.Fire(cmd)
