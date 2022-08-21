#!/usr/bin/env python3

import fire
from classes import *
import dotenv

dotenv.load_dotenv()


def cmd(transcript_file: str, type: str = 'srt', lang: str = None):
    transcript = Transcript.load_file(transcript_file)

    if type == 'srt':
        print(transcript.to_srt(lang=lang))
    else:
        print(transcript.to_ass(lang=lang))


if __name__ == "__main__":
    fire.Fire(cmd)
