#!/usr/bin/env python3

import json
import fire
from classes import *


def cmd(transcript_file: str, gap: float = None):
    transcript = Transcript.load_file(transcript_file)

    transcript.build_phrases(gap=gap)
    print(transcript.to_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    fire.Fire(cmd)
