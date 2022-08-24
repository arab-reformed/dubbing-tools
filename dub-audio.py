#!/usr/bin/env python3
import sys

from classes import Video
import os
import fire
from classes import *
import dotenv

dotenv.load_dotenv()

SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(project_path: str, video_file: str, lang: str, srt: bool = False, overwrite: bool = False, overlay_gain: int = -30):
    path = os.path.dirname(__file__)
    project_path = os.path.join(path, project_path)
    video_file = os.path.join(path, video_file)

    transcript = Transcript.load(project_path)

    video = Video(
        source_file=video_file,
        output_path=project_path,
        target_file=os.path.join(project_path, f"video-{lang}.mp4"),
        # srt_path=os.path.join(project_path, f"phrases-{lang}.srt")
    )

    video.dub_audio(
        transcript=transcript,
        lang=lang,
        overwrite=overwrite,
        overlay_gain=overlay_gain,
    )

    if not transcript.save():
        print("Error saving project file.", file=sys.stderr)


if __name__ == "__main__":
    fire.Fire(cmd)
