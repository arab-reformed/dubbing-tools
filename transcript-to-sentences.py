from dubber import parse_sentence_with_speaker
import json
import os
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def jsonify(result):
    json = []
    for i, section in enumerate(result['results']):
        section_alt = section['alternatives'][0]
        if 'transcript' in section_alt:
            import pprint
            # print(i)
            # pprint.pprint(section_alt)
            data = {
                "transcript": section_alt['transcript'],
                "end_time": section['resultEndTime'],
                "words": []
            }
            for word in section_alt['words']:
                data["words"].append({
                    "word": word['word'],
                    "start_time": word['startTime'],
                    "end_time": word['endTime'],
                    # "speaker_tag": word.speaker_tag
                })
            json.append(data)

    return json


def cmd(transcript_file: str):
    with open(transcript_file, 'r') as input:
        transcript = json.load(input)

    transcript = jsonify(transcript)

    sentences = parse_sentence_with_speaker(transcript, SOURCE_LANG)

    print(json.dumps(sentences, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
