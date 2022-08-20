#!/usr/bin/env python3

from functions import jsonify, textify
import json
import os
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(transcript_file: str):
    with open(transcript_file, 'r') as input:
        transcript = json.load(input)

    transcript = jsonify(transcript)

    print(textify(transcript))


if __name__ == "__main__":
    fire.Fire(cmd)
