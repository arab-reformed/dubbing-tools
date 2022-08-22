#!/usr/bin/env python3

import fire
from classes import *


def cmd(tts_file: str):
    transcript = Transcript.load_google_tts(tts_file)

    print(transcript.to_json(indent=2, ensure_ascii=False))


if __name__ == "__main__":
    fire.Fire(cmd)
