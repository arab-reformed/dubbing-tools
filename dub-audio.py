#!/usr/bin/env python3

from classes import Video
import os
import fire
from classes import PhrasesContainer

SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(project_path: str, video_file: str, lang: str, srt: bool = False, overwrite: bool = False):

    container = PhrasesContainer.load_file(os.path.join(project_path, f"phrases-{lang}.json"))

    video = Video(
        source_file=video_file,
        output_path=project_path,
        transcript=container,
        target_file=os.path.join(project_path, f"video-{lang}.mp4")
    )

    video.dub_audio(lang=lang)


if __name__ == "__main__":
    fire.Fire(cmd)
