#!/usr/bin/env python3

import fire
from classes import *
import dotenv

dotenv.load_dotenv()


def cmd(transcript_file: str, type: str = 'srt', lang: str = None, include_source: bool = False):
    transcript = Transcript.load_file(transcript_file)

    if type == 'srt':
        print(transcript.to_srt(lang=lang, include_source=include_source))
    else:
        print(transcript.to_ass(lang=lang, include_source=include_source))


if __name__ == "__main__":
    fire.Fire(cmd)
