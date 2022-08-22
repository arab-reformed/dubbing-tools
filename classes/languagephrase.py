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
import re


@dataclass_json
@dataclass
class LanguagePhrase:
    VOICES = {
        'ar': 'ar-XA-Wavenet-B',
    }

    lang: str
    text: str
    start_time: float = None
    end_time: float = None
    audio_file: str = None
    natural_duration: float = None

    def gap_between(self, next_phrase: 'LanguagePhrase'):
        return round(next_phrase.start_time - self.end_time, 2)

    def duration(self) -> Optional[float]:
        if self.start_time is not None and self.end_time is not None:
            return round(self.end_time - self.start_time, 2)
        return None

    def audio_speed(self):
        return self.natural_duration / self.duration()

    def speak(self, voice_name: str = None, speaking_rate: float = 1.0):

        if voice_name is None:
            voice_name = self.VOICES[self.lang]

        # Instantiates a client
        client = texttospeech.TextToSpeechClient()

        # Set the text input to be synthesized
        synthesis_input = texttospeech.SynthesisInput(text=self.get_text(self.lang))

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

        return response.audio_content

    def speak_under_duration(self, voice_name: str = None):

        base_audio = self.speak(voice_name=voice_name)
        assert len(base_audio)

        f = tempfile.NamedTemporaryFile(mode="w+b")
        f.write(base_audio)
        f.flush()

        self.audio_duration = AudioSegment.from_mp3(f.name).duration_seconds
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
            voice_name=voice_name,
            speaking_rate=ratio
        )

    def save_audio(self, output_path, overwrite: bool = False, use_duration: bool = True):
        language_path = os.path.join(output_path, self.lang)

        if not os.path.exists(language_path):
            os.mkdir(language_path)

        file = os.path.join(language_path, f"{self.id}.mp3")
        if overwrite or not os.path.exists(file):
            print(f"Generating: {file}", file=sys.stderr)
            if use_duration:
                audio = self.speak_under_duration()
            else:
                audio = self.speak()

            with open(file, 'wb') as f:
                f.write(audio)
                self.audio_file = file
        elif os.path.exists(file):
            self.audio_file = file

        # if self.target_duration is None and os.path.exists(self.audio_file):
        #     self.set_target_duration()

    def get_audio_duration(self) -> Optional[float]:
        if self.audio_file:
            return AudioSegment.from_mp3(self.audio_file).duration_seconds

        return None

    @staticmethod
    def time_to_str(seconds: float, milli_sep: str = '.') -> str:
        millisecs = seconds * 1000
        seconds, millisecs = divmod(millisecs, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%d:%02d:%02d%s%02d" % (hours, minutes, seconds, milli_sep, millisecs/10)

    def to_srt(self, source: 'SourceLanguagePhrase', include_source: bool = False) -> str:
        start = self.start_time if self.start_time else source.start_time
        end = self.end_time if self.end_time else source.end_time

        text = self.subtitle_text()
        if include_source:
            text = source.subtitle_text() + '\n' + text

        return f"{self.id}\n" \
               + self.time_to_str(start, milli_sep=',') \
               + " --> " \
               + self.time_to_str(end, milli_sep=',') \
               + f"\n{text}"

    def to_ass(self, source: 'SourceLanguagePhrase', style_name: str, include_source: bool = False):
        # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        # Dialogue: 0,0:00:00.63,0:00:04.56,Arabic,,0,0,0,,أود أن ألفت انتباهكم إلى خمسة أمور
        start = self.start_time if self.start_time else source.start_time
        end = self.end_time if self.end_time else source.end_time

        text = self.subtitle_text()
        if include_source:
            text = '\u202d' + source.subtitle_text() + '\\N' + text

        return f"Dialogue: 0,{self.time_to_str(start)},{self.time_to_str(end)},{style_name},,0,0,0,,{text}"

    def subtitle_text(self) -> str:
        def number_replace(m: re.Match):
            num = str(m.group(0))
            # print('Number:', num, file=sys.stderr)
            num = num.replace('0', '٠')
            num = num.replace('1', '١')
            num = num.replace('2', '٢')
            num = num.replace('3', '٣')
            num = num.replace('4', '٤')
            num = num.replace('5', '٥')
            num = num.replace('6', '٦')
            num = num.replace('7', '٧')
            num = num.replace('8', '٨')
            num = num.replace('9', '٩')

            # num = '\u202d' + num + '\u202e'

            reverse = ''
            for i in range(len(num)):
                reverse = num[i] + reverse

            return reverse

        text = self.text
        text = text.replace("\n", '\\N')

        if self.lang == 'ar':
            loop = 1
            while loop:
                (text, loop) = re.subn(
                    r'(?P<start>(^|\\N)"*)(?P<punc>[.،:])(?P<line>[^.].*?)(?P<end>$|\\N)',
                    r'\g<start>\g<line>\g<punc>\g<end>',
                    text
                )
            text = re.sub(r'\\N', '\\\\N\u202e', text, flags=re.UNICODE)
            text = re.sub(r'\.', '\u202e.', text, flags=re.UNICODE)
            text = re.sub(r'،', '\u202e،', text, flags=re.UNICODE)
            text = re.sub(r'\(', '\u202e(', text, flags=re.UNICODE)
            text = re.sub(r'\d+', number_replace, text)
            text = '\u202e' + text

        return text
