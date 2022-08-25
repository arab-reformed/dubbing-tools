import sys
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip, CompositeVideoClip
from moviepy.video.tools.subtitles import SubtitlesClip, TextClip
import tempfile
from pydub import AudioSegment
from google.cloud import texttospeech
from typing import Optional


@dataclass_json
@dataclass
class Audio:
    file_name: str
    duration: Optional[float] = None

    VOICES = {
        'ar': 'ar-XA-Wavenet-B',
    }

    def file_exists(self):
        return os.path.exists(self.file_name)

    def get_duration(self) -> Optional[float]:
        if self.duration is not None and not self.file_exists():
            self.duration = None

        elif self.duration is None and self.file_exists():
            self.duration = AudioSegment.from_mp3(self.file_name).duration_seconds

        return self.duration

    def tts_audio(self, text: str, lang: str, voice_name: str = None, speaking_rate: float = 1.0, overwrite: bool = False):
        print(f"Getting audio: {text}", file=sys.stderr)
        if not overwrite and os.path.exists(self.file_name):
            with open(self.file_name, 'r+b') as f:
                audio = f.read()
                f.close()
                return audio

        if voice_name is None:
            voice_name = self.VOICES[lang]

        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=text)

        voice = texttospeech.VoiceSelectionParams(
            language_code=lang,
            name=voice_name
        )

        # Select the type of audio file you want returned
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            sample_rate_hertz=24000,
            speaking_rate=speaking_rate
        )

        # Perform the text-to-speech request on the text input with the selected
        # voice parameters and audio file type
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )

        self.save(response.audio_content)

        return response.audio_content

    def save(self, audio) -> bool:
        if self.file_name is not None:
            with open(self.file_name, 'wb') as f:
                f.write(audio)
                f.close()
                self.duration = None
                self.get_duration()
                return True

        return False
