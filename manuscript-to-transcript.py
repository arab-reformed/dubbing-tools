from functions import jsonify
import json
import os
import fire


SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(json_file: str, text_file: str):
    with open(json_file, 'r') as f:
        transcript = json.load(f)

    transcript = jsonify(transcript)

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
                    if j < len(words)-1 and words[j][-1] != ' ' and words[j+1][0] != ' ':
                        timing['word'] = (words[j] + words[j+1]).strip()
                        timing['end_time'] = transcript[i]['words'][k+1]['end_time']
                        k += 1
                        j += 1
                    else:
                        timing['word'] = words[j].strip()

                    timing['start_time'] = float(timing['start_time'].replace('s', ''))
                    timing['end_time'] = float(timing['end_time'].replace('s', ''))
                    timings.append(timing)
                    j += 1
                    k += 1

    print(json.dumps(timings, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
