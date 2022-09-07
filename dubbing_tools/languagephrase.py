from typing import Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, Undefined, CatchAll, DataClassJsonMixin
from .audio import Audio
from .constants import *
import os
import re
from .timings import Timings
from .phrasetiming import PhraseTiming

MINIMUM_GAP = 0.3


# @dataclass_json
@dataclass
class LanguagePhrase(DataClassJsonMixin):
    lang: str
    text: str
    id: int = None
    timings: Timings = field(default_factory=Timings)
    natural_audio: Audio = None
    duration_audio: Audio = None
    start_time: float = None
    end_time: float = None
    freeze_time: float = None
    freeze_duration: float = None

    # extras: CatchAll = None

    ASS_CLASSES = {
        'ar': 'Arabic',
        'en': 'Latin',
        'pt': 'Latin',
    }

    # def __post_init__(self):
    #     if hasattr(self, 'start_time') and self.timings.get() is None:
    #         # print(f"{self.id}  {self.lang}  {self.text}")
    #         self.timings.set(timing=PhraseTiming(
    #             start_time=self.start_time,
    #             end_time=self.end_time if hasattr(self, 'end_time') else None,
    #             freeze_time=self.freeze_time if hasattr(self, 'freeze_time') else None,
    #             freeze_duration=self.freeze_duration if hasattr(self, 'freeze_duration') else None,
    #         ))
    #         del self.start_time
    #         del self.end_time
    #         del self.freeze_time
    #         del self.freeze_duration

    # def __setattr__(self, key, value):
    #     try:
    #         if key == 'text' and self.text != value:
    #             if self.natural_audio is not None:
    #                 self.natural_audio.changed = True
    #             if self.duration_audio is not None:
    #                 self.duration_audio.changed = True
    #     except Exception as e:
    #         print(e)
    #         raise e
    #
    #     super().__setattr__(key, value)

    def set_text(self, text):
        if text != self.text:
            self.mark_audio_changed()
        self.text = text

    def get_timing(self, timing_scheme: str = None) -> PhraseTiming:
        return self.timings.get(timing_scheme)

    def audio_speed(self, timing_scheme: str = None):
        return round(self.natural_audio.duration / self.timings.get(timing_scheme).duration(), 2)

    def mark_audio_changed(self):
        self.mark_natural_audio_changed()
        self.mark_duration_audio_changed()

    def mark_natural_audio_changed(self):
        if self.natural_audio is not None:
            self.natural_audio.changed = True

    def mark_duration_audio_changed(self):
        if self.duration_audio is not None:
            self.duration_audio.changed = True

    def get_tts_natural_audio(self, service: str = SERVICE_AZURE, overwrite: bool = False, voice_name: str = None):
        if self.natural_audio is None or overwrite:
            self.natural_audio = Audio(file_name=self.natural_audio_fullpath(service=service))

        overwrite = overwrite or self.natural_audio.changed or self.natural_audio.is_null()

        self.natural_audio.tts_audio(
            text=self.text,
            lang=self.lang,
            service=service,
            voice_name=voice_name,
            overwrite=overwrite,
        )
        self.natural_audio.changed = False

    def get_tts_duration_audio(self, timing_scheme: str, service: str = SERVICE_AZURE, overwrite: bool = False, voice_name: str = None):
        # print(f"{self.id} {self.duration_audio}")
        if self.duration_audio is None or overwrite:
            # print(f"{self.id}")
            self.duration_audio = Audio(file_name=self.audio_fullpath(service=service))

        overwrite = overwrite or self.duration_audio.changed

        if self.natural_audio is None:
            self.get_tts_natural_audio(
                service=service,
                overwrite=overwrite,
                voice_name=voice_name,
            )

        ratio = self.natural_audio.duration / self.timings.get(timing_scheme).duration()

        # if the audio fits, return it
        if ratio <= 1.0:
            ratio = 1.0

        # round to one decimal point and go a little faster to be safe,
        ratio = round(ratio, 1)
        if ratio > 3.0:
            ratio = 3.0

        self.duration_audio.tts_audio(
            text=self.text,
            lang=self.lang,
            voice_name=voice_name,
            speaking_rate=ratio,
            overwrite=overwrite,
        )

        self.duration_audio.changed = False

    def audio_filename(self):
        return f"{str(self.id).rjust(5, '0')}.mp3"

    def natural_audio_path(self, service: str) -> str:
        # print(os.getcwd(), file=sys.stderr)
        path = os.path.join(SUBDIR_AUDIO, self.lang, service, 'natural')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def natural_audio_fullpath(self, service: str) -> str:
        return os.path.join(self.natural_audio_path(service=service), self.audio_filename())

    def audio_path(self, service: str) -> str:
        path = os.path.join(SUBDIR_AUDIO, self.lang, service, 'duration')
        if not os.path.exists(path):
            os.makedirs(path)
        return path

    def audio_fullpath(self, service: str) -> str:
        return os.path.join(self.audio_path(service=service), self.audio_filename())

    def get_audio_duration(self) -> Optional[float]:
        if self.duration_audio is None:
            return None
        return self.duration_audio.get_duration()

    def get_natural_audio_duration(self) -> Optional[float]:
        if self.natural_audio is None:
            return None
        return self.natural_audio.get_duration()

    @staticmethod
    def time_to_str(seconds: float, milli_sep: str = '.') -> str:
        millisecs = seconds * 1000
        seconds, millisecs = divmod(millisecs, 1000)
        minutes, seconds = divmod(seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return "%d:%02d:%02d%s%02d" % (hours, minutes, seconds, milli_sep, millisecs/10)

    def to_srt(self, source: 'SourceLanguagePhrase', timing_scheme: str = None, timing: PhraseTiming = None, include_source: bool = False) -> str:
        if timing is not None:
            start = timing.start_time
            end = timing.end_time
        else:
            start = self.timings.get(timing_scheme).start_time
            end = self.timings.get(timing_scheme).end_time

        text = self.subtitle_text()
        if include_source:
            text = source.subtitle_text() + '\n' + text

        return f"{self.id}\n" \
               + self.time_to_str(start, milli_sep=',') \
               + " --> " \
               + self.time_to_str(end, milli_sep=',') \
               + f"\n{text}"

    def to_ass(self, start: float, end: float, source: 'SourceLanguagePhrase' = None, debug: bool = False):
        # Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
        # Dialogue: 0,0:00:00.63,0:00:04.56,Arabic,,0,0,0,,أود أن ألفت انتباهكم إلى خمسة أمور

        text = self.subtitle_text()
        if source is not None:
            text = '\u202d' + source.subtitle_text() + '\\N' + text

        if debug:
            text = f"{self.id}: {text}"

        return f"Dialogue: 0,{self.time_to_str(start)},{self.time_to_str(end)},{self.ASS_CLASSES[self.lang]},,0,0,0,,{text}"

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

        # remove periods at end of sentences
        text = re.sub('\\.$', '', text, re.MULTILINE)

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
