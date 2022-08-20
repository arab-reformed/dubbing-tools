#!/usr/bin/env python3
import sys

from dubber import get_transcripts_json, parse_sentence_with_speaker
import json
import os
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(audio_file: str):
    base_name = os.path.split(audio_file)[-1].split('.')[0]

    transcripts = get_transcripts_json(
        audio_file,
        SOURCE_LANG,
        phraseHints=PHRASE_HINTS,
        speakerCount=1
    )

    transcript_file = f"{base_name}-transcript.json"
    json.dump(transcripts, open(transcript_file, "w"))
    print(f"Wrote {transcript_file}")

    sentences = parse_sentence_with_speaker(transcripts, SOURCE_LANG)
    sentences_file = f"{base_name}-sentences.json"

    with open(sentences_file, "w") as f:
        json.dump(sentences, f)
    print(f"Wrote {sentences_file}", file=sys.stderr)


if __name__ == "__main__":
    fire.Fire(cmd)
