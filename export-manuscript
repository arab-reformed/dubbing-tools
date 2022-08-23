#!/usr/bin/env python3

from functions import jsonify, textify
import json
import os
import fire
from classes import *

SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(transcript_file: str):
    transcript = Transcript.load_file(transcript_file)

    print(transcript.to_manuscript())


if __name__ == "__main__":
    fire.Fire(cmd)
