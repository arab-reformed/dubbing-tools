#!/usr/bin/env python3

import fire
from classes import *
import sys


def cmd(transcript_path: str, gap: float = None):
    transcript = Transcript.load(transcript_path)

    transcript.build_phrases(gap=gap)

    if not transcript.save(transcript_path):
        print("Error saving transcript", file=sys.stderr)


if __name__ == "__main__":
    fire.Fire(cmd)
