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


def textify(transcript):
    txt = ''
    for section in transcript:
        section_text = ''
        for word in section['words']:
            section_text += (' ` ' if section_text else '') + word['word']

        txt += f"{section_text}\n\n"

    return txt


def cmd(transcript_file: str, sentences_file: str):
    with open(transcript_file, 'r') as input:
        transcript = json.load(input)

    transcript = _jsonify(transcript)

    sentences = parse_sentence_with_speaker(transcript, SOURCE_LANG)

    with open(sentences_file, 'w') as f:
        json.dump(sentences, f)

    text_file = sentences_file.replace('.json', '') + '.txt'
    # with open(text_file, 'w') as f:
    #     f.write(textify(transcript))


if __name__ == "__main__":
    fire.Fire(cmd)
