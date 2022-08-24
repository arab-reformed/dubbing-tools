#!/usr/bin/env python3

from classes import Video
import os
import fire
from classes import *
import dotenv

dotenv.load_dotenv()

SOURCE_LANG = 'en-US'
SPEAKER_COUNT = 1
PHRASE_HINTS = []


def cmd(project_path: str, video_file: str, lang: str, srt: bool = False, overwrite: bool = False):
    path = os.path.dirname(__file__)
    project_path = os.path.join(path, project_path)
    video_file = os.path.join(path, video_file)

    transcript = Transcript.load(project_path)

    video = Video(
        source_file=video_file,
        output_path=project_path,
        transcript=transcript,
        target_file=os.path.join(project_path, f"video-{lang}.mp4"),
        srt_path=os.path.join(project_path, f"phrases-{lang}.srt")
    )

    video.dub_audio(lang=lang, overwrite=overwrite)

    print(transcript.to_json(indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
