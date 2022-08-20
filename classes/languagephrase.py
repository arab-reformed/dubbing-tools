import sys
from pydub import AudioSegment
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .word import Word
import tempfile
import os


@dataclass_json
@dataclass
class LanguagePhrase:
    SRC_LANG = 'en'
    TARGET_LANG = 'ar'
    ALL_LANGS = 'all'
    VOICES = {
        'ar': 'ar-XA-Wavenet-B',
    }

    lang: str
    text: str
    start_time: float = None
    end_time: float = None
    audio_file: str = None

    def gap_between(self, next_phrase: 'LanguagePhrase'):
        return round(next_phrase.start_time - self.end_time, 2)

    def word_count(self) -> int:
        return self.end_word - self.start_word + 1

    def duration(self) -> float:
        return round(self.end_time - self.start_time, 2)

    def to_srt(self, lang: str) -> str:
        def _srt_time(seconds):
            millisecs = seconds * 1000
            seconds, millisecs = divmod(millisecs, 1000)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            return "%d:%d:%d,%d" % (hours, minutes, seconds, millisecs)

        return f"{self.id}\n" + _srt_time(self.start_time) + " --> " \
               + _srt_time(self.end_time) + f"\n{self.get_text(lang)}"

    def speak(self, voice_name: str = None, speaking_rate: float = 1.0):

        if voice_name is None:
            voice_name = self.VOICES[self.lang]

        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=self.get_text(lang))

        voice = texttospeech.VoiceSelectionParams(
            language_code=lang,
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

        return response.audio_content

    def speak_under_duration(self, lang: str, voice_name: str = None):

        base_audio = self.speak(lang, voice_name=voice_name)
        assert len(base_audio)

        f = tempfile.NamedTemporaryFile(mode="w+b")
        f.write(base_audio)
        f.flush()

        self.target_duration = AudioSegment.from_mp3(f.name).duration_seconds
        f.close()
        ratio = self.target_duration / self.duration()

        # if the audio fits, return it
        if ratio <= 1:
            return base_audio

        # round to one decimal point and go a little faster to be safe,
        ratio = round(ratio, 1)
        if ratio > 4:
            ratio = 4

        return self.speak(
            lang=lang,
            voice_name=voice_name,
            speaking_rate=ratio
        )

    def save_audio(self, output_path, lang: str, overwrite: bool = False, use_duration: bool = True):
        language_path = os.path.join(output_path, lang)

        if not os.path.exists(language_path):
            os.mkdir(language_path)

        file = os.path.join(language_path, f"{self.id}.mp3")
        if overwrite or not os.path.exists(file):
            print(f"Generating: {file}", file=sys.stderr)
            if use_duration:
                audio = self.speak_under_duration(lang=lang)
            else:
                audio = self.speak(lang=lang)

            with open(file, 'wb') as f:
                f.write(audio)
                self.audio_file = file
        elif os.path.exists(file):
            self.audio_file = file

        # if self.target_duration is None and os.path.exists(self.audio_file):
        #     self.set_target_duration()

    def get_target_duration(self) -> Optional[float]:
        if self.audio_file:
            return AudioSegment.from_mp3(self.audio_file).duration_seconds

        return None
