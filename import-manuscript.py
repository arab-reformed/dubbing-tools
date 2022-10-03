#!/usr/bin/env python3

from dubbing_tools import *
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(transcript_path: str, manuscript_file: str):

    transcript = Transcript.load(transcript_path)

    i = 0
    with open(manuscript_file, 'r') as f:
        for line in f.readlines():
            if len(line.strip()) == 0:
                i += 1

            else:
                words = line.split('`')
                j = 0
                k = 0
                while j < len(words):
                    word = transcript.words[k]
                    word.set_word(words[j].strip())
                    if j < len(words)-1 and words[j][-1] != ' ' and words[j+1][0] != ' ':
                        word.set_word((words[j] + words[j+1]).strip())
                        word.end_time = transcript.words[k+1].end_time
                        del transcript.words[k+1]
                        j += 1

                    j += 1
                    k += 1

    transcript.save()


if __name__ == "__main__":
    fire.Fire(cmd)
