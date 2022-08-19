from sentences import jsonify
import json
import os
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(json_file: str, text_file: str):
    with open(json_file, 'r') as f:
        tramscript = json.load(f)

    transcript = jsonify(tramscript)

    i = 0
    with open(text_file, 'r') as f:
        section_transcript = ''
        for line in f.readlines():
            if len(line.strip()) == 0:
                if section_transcript:
                    transcript[i]['transcript'] = section_transcript

                section_transcript = ''
                i += 1
            else:
                words = line.split('`')
                j = 0
                k = 0
                while j < len(words):
                    if j < len(words)-1 and words[j][-1] != ' ' and words[j+1][0] != ' ':
                        transcript[i]['words'][k]['word'] = (words[j] + words[j+1]).strip()
                        transcript[i]['words'][k]['end_time'] = transcript[i]['words'][k+1]['end_time']
                        del transcript[i]['words'][k+1]
                        j += 2
                    else:
                        transcript[i]['words'][k]['word'] = words[j].strip()
                        j += 1

                    section_transcript += (' ' if section_transcript else '') + transcript[i]['words'][k]['word']
                    k += 1

        if section_transcript:
            transcript[i]['transcript'] = section_transcript

    print(json.dumps(transcript, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
