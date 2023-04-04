#!/usr/bin/env python3

import fire
from dubbing_tools.audio import *


def cmd(text: str, mp3_file: str, speaking_rate: float = 1.0, voice_name: str = 'ar-EG-ShakirNeural'):
	audio = Audio(file_name=mp3_file)

	audio.tts_azure_audio(text, voice_name=voice_name, speaking_rate=speaking_rate, lang='ar')


if __name__ == "__main__":
	fire.Fire(cmd)
