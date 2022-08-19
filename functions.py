
def jsonify(result):
    if type(result) == list:
        return result

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


def get_phrases(words: list, lang: str, gap: float = 1.0):

    phrases = []
    phrase = {}
    for i, word in enumerate(words):
        if not phrase:
            phrase = {
                lang: [word['word']],
                # 'speaker': word['speaker_tag'],
                'start_time': word['start_time'],
                'end_time': word['end_time']
            }
        # If we have a new speaker, save the sentence and create a new one:
        elif 'speaker_tag' in word and word['speaker_tag'] != phrase['speaker']:
            phrase[lang] = ' '.join(phrase[lang])
            phrases.append(phrase)
            phrase = {
                lang: [word['word']],
                'speaker': word['speaker_tag'],
                'start_time': word['start_time'],
                'end_time': word['end_time']
            }
        else:
            phrase[lang].append(word['word'])
            phrase['end_time'] = word['end_time']

        # If there's greater than one second gap, assume this is a new sentence
        if word['word'][-1] in [',', '.', '?', '!'] or \
                i < len(words)-1 and word['end_time'] - words[i + 1]['start_time'] > gap:
            phrase[lang] = ' '.join(phrase[lang])
            phrases.append(phrase)
            phrase = {}

    if phrase:
        phrase[lang] = ' '.join(phrase[lang])
        phrases.append(phrase)
        phrase = {}

    return phrases
