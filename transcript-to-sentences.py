from dubber import parse_sentence_with_speaker
from functions import jsonify
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

    sentences = parse_sentence_with_speaker(transcript, SOURCE_LANG)

    print(json.dumps(sentences, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
