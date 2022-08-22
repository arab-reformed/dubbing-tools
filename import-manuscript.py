#!/usr/bin/env python3

from functions import jsonify
from classes import *
import json
import os
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(json_file: str, text_file: str):

    transcript = Transcript.load_file(json_file)

    timings = []

    i = 0
    with open(text_file, 'r') as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                i += 1

            else:
                words = line.split('`')
                j = 0
                k = 0
                while j < len(words):
                    timing = transcript[i]['words'][k]
                    word = Word(
                        id=len(timings),
                        word=words[j].strip(),
                        start_time=Word.secs_to_float(timing['start_time']),
                        end_time=Word.secs_to_float(timing['end_time']),
                    )
                    if j < len(words)-1 and words[j][-1] != ' ' and words[j+1][0] != ' ':
                        word.set_word((words[j] + words[j+1]).strip())
                        word.end_time = Word.secs_to_float(transcript[i]['words'][k+1]['end_time'])
                        k += 1
                        j += 1

                    timings.append(word)
                    j += 1
                    k += 1

    print(Word.schema().dumps(timings, many=True, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
