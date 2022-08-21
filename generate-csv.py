#!/usr/bin/env python3

import sys
import fire
from classes import *
import dotenv
import csv

dotenv.load_dotenv()


def cmd(transcript_file: str, lang: str):
    transcript = Transcript.load_file(transcript_file)

    writer = csv.writer(sys.stdout)
    writer.writerows(transcript.to_csv(lang))


if __name__ == "__main__":
    fire.Fire(cmd)
