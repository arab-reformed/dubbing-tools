#!/usr/bin/env python3

from dubber import decode_audio
import json
import os
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(video_file: str):
    base_name = os.path.split(video_file)[-1].split('.')[0]

    decode_audio(video_file, f"{base_name}.wav")


if __name__ == "__main__":
    fire.Fire(cmd)
