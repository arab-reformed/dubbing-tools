from typing import List, Optional
import sys
from dubbing_tools import *
import os
from dubbing_tools.constants import *

__all__ = [
    'subtitled_video_fullpath',
    'subtitles_fullpath',
    'video_fullpath',
    'video_source_fullpath',
]


def video_source_fullpath() -> str:
    return os.path.join(SUBDIR_VIDEO, f"source.mp4")


def video_fullpath(lang: str, timing_scheme: str) -> str:
    return os.path.join(SUBDIR_VIDEO, f"video-{timing_scheme}-{lang}.mp4")


def subtitled_video_fullpath(lang: str, timing_scheme: str, subtitle_lang: str) -> str:
    return os.path.join('subtitled', f"video-{timing_scheme}-{lang}.{subtitle_lang}.mp4")


def subtitles_fullpath(lang: str, timing_scheme: str, subtitle_lang: str, sub_type: str = 'ass') -> str:
    return os.path.join(SUBDIR_VIDEO, f"video-{timing_scheme}-{lang}.{subtitle_lang}.{sub_type}")


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
