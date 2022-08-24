import sys
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from classes import Phrase, Transcript
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
import tempfile
from pydub import AudioSegment
from google.cloud import texttospeech
from typing import Optional


@dataclass
class Audio:
    lang: str
    overwrite: bool = True
    file_name: str = None

    VOICES = {
        'ar': 'ar-XA-Wavenet-B',
    }

    def tts_audio(self, text: str, voice_name: str = None, speaking_rate: float = 1.0):
        if not self.overwrite and os.path.exists(self.file_name):
            with open(self.file_name, 'r+b') as f:
                audio = f.read()
                f.close()
                return audio

        if voice_name is None:
            voice_name = self.VOICES[self.lang]

        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=self.lang,
            name=voice_name
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=speaking_rate
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        if self.file_name:
            self.save(response.audio_content)

        return response.audio_content

    def get_audio_duration(self) -> Optional[float]:
        if os.path.exists(self.file_name):
            return AudioSegment.from_mp3(self.file_name).duration_seconds

        return None

    def save(self, audio):
        if self.file_name is not None and self.overwrite or not os.path.exists(self.file_name):
            with open(self.file_name, 'wb') as f:
                f.write(audio)
                f.close()
