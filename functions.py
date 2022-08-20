from typing import List, Optional
import sys
from classes import *


def jsonify(result):
    if type(result) == list:
        return result

    json = []
    for i, section in enumerate(result['results']):
        section_alt = section['alternatives'][0]
        if 'transcript' in section_alt:
            # import pprint
            # print(i, file=sys.stderr)
            # pprint.pprint(section_alt, file=sys.stderr)
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


def get_phrases(words: List[Word], lang: str, gap: float = 1.0):
    clauses = [
        ['through', 'that', 'which', 'whereby', 'is'],
        ['of', 'by', 'about', 'from', 'in', 'into', 'for']
    ]

    phrases = []
    phrase = None
    reason = None
    for i, word in enumerate(words):
        if not phrase:
            phrase = OldPhrase(
                id=len(phrases),
                src_lang=word.word,
                start_time=word.start_time,
                end_time=word.end_time,
                start_word=i,
                end_word=i,
                reason=reason
            )

        else:
            phrase.src_lang += ' ' + word.word
            phrase.end_time = word.end_time
            phrase.end_word = i

        if i < len(words)-1:
            reason = word.break_reason(next_word=words[i+1], gap=gap)
        else:
            reason = None

        # If there's greater than one second gap, assume this is a new sentence
        if reason is not None:
            phrases.append(phrase)
            phrase = None

    if phrase:
        phrases.append(phrase)

    # Process phrases to make sure none are too long
    for small_gap in [0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0.0]:
        changed = True
        while changed:
            changed = False
            shortened = []
            print(f"gap = {small_gap}", file=sys.stderr)
            for p, phrase in enumerate(phrases):
                shortened.append(phrase)
                print(f"Phrase: {p}", file=sys.stderr)
                if phrase.word_count() > 6:
                    for i in range(phrase.start_word+3, phrase.end_word-3):
                        reason = words[i].break_reason(next_word=words[i+1], gap=small_gap)
                        # print(i, reason, file=sys.stderr)
                        if reason is not None:
                            new = phrase.split(words, split_at=i)
                            new.reason = reason
                            shortened.append(new)
                            changed = True
                            break

            phrases = shortened

    for intros in clauses:
        changed = True
        while changed:
            changed = False
            shortened = []
            for phrase in phrases:
                shortened.append(phrase)
                if phrase.word_count() > 6:
                    for i in range(phrase.start_word+3, phrase.end_word-3):
                        if words[i].word in intros:
                            new = phrase.split(words, split_at=i-1)
                            new.reason = words[i].word
                            shortened.append(new)
                            changed = True
                            break

            phrases = shortened

    # renumber words
    for i, phrase in enumerate(phrases):
        phrase.id = i

    return phrases
