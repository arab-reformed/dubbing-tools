#!/usr/bin/env python3

from dubbing_tools.transcript import *
import sys
import os
import fire


def cmd(transcript_path: str, lang: str):

    transcript = Transcript.load(transcript_path)

    for phrase in transcript.phrases:
        target = phrase.get_target(lang)
        if '\n' in target.text:
            print(f"Id: {target.id}")
            target.mark_audio_changed()

    if not transcript.save():
        print("Error saving project file.", file=sys.stderr)


if __name__ == "__main__":
    fire.Fire(cmd)
