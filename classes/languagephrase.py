import sys
from pydub import AudioSegment
from google.cloud import texttospeech
from google.cloud import translate_v2 as translate
from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from .audio import Audio
import tempfile
import os
import re


@dataclass_json
@dataclass
class LanguagePhrase:
    lang: str
    text: str
    id: int = None
    start_time: float = None
    end_time: float = None
    natural_audio: Audio = None
    duration_audio: Audio = None

    AUDIO_SUBDIR = 'audio-clips'

    def gap_between(self, next_phrase: 'LanguagePhrase'):
        return round(next_phrase.start_time - self.end_time, 2)

    def duration(self) -> Optional[float]:
        if self.start_time is not None and self.end_time is not None:
            return round(self.end_time - self.start_time, 2)
        return None

    def reset_timing(self, source: 'LanguagePhrase'):
        self.start_time = source.start_time
        self.end_time = source.end_time

    def shift(self, increment: float) -> bool:
        # TODO: make sure not shifted past the end of the video
        if self.start_time - increment < 0:
            return False

        self.start_time += increment
        self.end_time += increment
        return True

    def move_start(self, increment: float) -> bool:
        if self.start_time - increment < 0:
            return False
        self.start_time += increment
        return True

    def move_end(self, increment: float) -> bool:
        # TODO: make sure not shifted past the end of the video
        self.end_time += increment
        return True

    def audio_speed(self):
        return round(self.natural_audio.duration / self.duration(),2)

    def get_tts_natural_audio(self, overwrite: bool = False, voice_name: str = None):
        if self.natural_audio is None:
            self.natural_audio = Audio(file_name=self.natural_audio_fullpath())

        base_audio = self.natural_audio.tts_audio(
            text=self.text,
            lang=self.lang,
            voice_name=voice_name,
            overwrite=overwrite,
        )
        assert len(base_audio)

        return base_audio

    def get_tts_duration_audio(self, overwrite: bool = False, voice_name: str = None):
        if self.duration_audio is None:
            self.duration_audio = Audio(self.audio_fullpath())

        if self.natural_audio is None:
            self.get_tts_natural_audio(
                overwrite=overwrite,
                voice_name=voice_name,
            )

        ratio = self.natural_audio.duration / self.duration()

        # if the audio fits, return it
        if ratio <= 1:
            return self.get_tts_natural_audio(
                overwrite=overwrite,
                voice_name=voice_name
            )

        # round to one decimal point and go a little faster to be safe,
        ratio = round(ratio, 1)
        if ratio > 4:
            ratio = 4

        return self.duration_audio.tts_audio(
            text=self.text,
            lang=self.lang,
            voice_name=voice_name,
            speaking_rate=ratio,
            overwrite=overwrite,
        )

    def audio_filename(self):
        return f"{str(self.id).rjust(5, '0')}.mp3"

    def natural_audio_path(self) -> str:
        # print(os.getcwd(), file=sys.stderr)
        path = os.path.join(self.AUDIO_SUBDIR, self.lang, 'natural')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def natural_audio_fullpath(self) -> str:
        return os.path.join(self.natural_audio_path(), self.audio_filename())

    def audio_path(self) -> str:
        path = os.path.join(self.AUDIO_SUBDIR, self.lang, 'duration')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def audio_fullpath(self) -> str:
        return os.path.join(self.audio_path(), self.audio_filename())

    def get_audio_duration(self) -> Optional[float]:
        if self.duration_audio is None:
            self.duration_audio = Audio(file_name=self.natural_audio_fullpath())
        return self.duration_audio.get_duration()

    def get_natural_audio_duration(self) -> Optional[float]:
        if self.natural_audio is None:
            self.natural_audio = Audio(file_name=self.audio_fullpath())
        return self.natural_audio.get_duration()

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
