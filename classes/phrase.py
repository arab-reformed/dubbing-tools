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
class Phrase:
    id: int
    src_lang: str
    start_time: float
    end_time: float
    start_word: int
    end_word: int
    target_lang: str = None
    reason: str = None
    audio_file: str = None
    text = {}
    SRC_LANG = 'en'
    TARGET_LANG = 'ar'
    ALL_LANGS = 'all'
    VOICES = {
        'ar': 'ar-XA-Wavenet-B',
    }

    def set_text(self, lang: str, text: str):
        if lang == self.SRC_LANG:
            self.src_lang = text
        elif lang == self.TARGET_LANG:
            self.target_lang = text

        self.text[lang] = text

    def word_count(self) -> int:
        return self.end_word - self.start_word + 1

    def duration(self) -> float:
        return round(self.end_time - self.start_time, 2)

    def split(self, words: List[Word], split_at: int) -> 'Phrase':
        next = Phrase(
            id=-1,
            src_lang=' '.join([w.word for w in words[split_at+1:self.end_word+1]]),
            start_time=words[split_at+1].start_time,
            end_time=words[self.end_word].end_time,
            start_word=split_at+1,
            end_word=self.end_word
        )
        self.src_lang = ' '.join([w.word for w in words[self.start_word:split_at+1]])
        self.end_time = words[split_at].end_time
        self.end_word = split_at

        return next

    @classmethod
    def words_to_phrase(cls, words: List[Word], start_word: int):
        return Phrase(
            src_lang=' '. join([w.word for w in words]),
            start_time=words[0].start_time,
            end_time=words[-1].end_time,
            start_word=start_word,
            end_word=start_word+len(words)-1
        )

    def translate_text(self, target_lang, source_lang=None):
        translate_client = translate.Client()
        result = translate_client.translate(
            self.src_lang,
            format_='text',
            target_language=target_lang,
            source_language=source_lang
        )

        self.target_lang = result['translatedText']

    def get_text(self, lang: str) -> Optional[str]:
        text = None
        if lang == self.SRC_LANG:
            text = self.src_lang
        elif lang == self.ALL_LANGS:
            text = f"{self.src_lang}\n{self.target_lang}"
        elif lang == self.TARGET_LANG:
            text = self.target_lang

        return text

    def to_srt(self, lang: str) -> str:
        def _srt_time(seconds):
            millisecs = seconds * 1000
            seconds, millisecs = divmod(millisecs, 1000)
            minutes, seconds = divmod(seconds, 60)
            hours, minutes = divmod(minutes, 60)
            return "%d:%d:%d,%d" % (hours, minutes, seconds, millisecs)

        return f"{self.id}\n" + _srt_time(self.start_time) + " --> " \
               + _srt_time(self.end_time) + f"\n{self.get_text(lang)}"

    def speak(self, lang: str, voice_name: str = None, speaking_rate: float = 1.0):

        if voice_name is None:
            voice_name = self.VOICES[lang]

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

        base_duration = AudioSegment.from_mp3(f.name).duration_seconds
        f.close()
        ratio = base_duration / self.duration()

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

        if os.path.exists(language_path):
            os.mkdir(language_path)

        file = os.path.join(language_path, f"{self.id}.mp3")
        if overwrite or os.path.isfile(file):
            if use_duration:
                audio = self.speakUnderDuration(lang=lang)
            else:
                audio = self.speak(lang=lang)

            with open(file, 'wb') as f:
                f.write(audio)
                self.audio_file = file
