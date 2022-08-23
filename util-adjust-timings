#!/usr/bin/env python3

import fire
from classes import *


def cmd(transcript_file: str, lang: str):
    transcript = Transcript.load_file(transcript_file)

    transcript.adjust_timings(lang=lang)
    print(transcript.to_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    fire.Fire(cmd)
