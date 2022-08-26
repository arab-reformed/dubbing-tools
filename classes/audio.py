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
import azure.cognitiveservices.speech as speechsdk
from .constants import *


@dataclass_json
@dataclass
class Audio:
    file_name: str
    duration: Optional[float] = None

    def file_exists(self):
        return os.path.exists(self.file_name)

    def get_duration(self, from_file: bool = False) -> Optional[float]:
        if self.duration is not None and not self.file_exists():
            self.duration = None

        elif (from_file or self.duration is None) and self.file_exists():
            self.duration = AudioSegment.from_mp3(self.file_name).duration_seconds

        return self.duration

    def tts_audio(self,
                  text: str,
                  lang: str,
                  service: str = SERVICE_AZURE,
                  voice_name: str = None,
                  speaking_rate: float = 1.0,
                  overwrite: bool = False
                  ):
        if service == SERVICE_GOOGLE:
            self.tts_google_audio(
                text=text,
                lang=lang,
                voice_name=voice_name,
                speaking_rate=speaking_rate,
                overwrite=overwrite,
            )
        elif service == SERVICE_AZURE:
            self.tts_azure_audio(
                text=text,
                lang=lang,
                voice_name=voice_name,
                speaking_rate=speaking_rate,
                overwrite=overwrite,
            )

    def tts_google_audio(self, text: str, lang: str, voice_name: str = None, speaking_rate: float = 1.0, overwrite: bool = False):
        print(f"Getting audio: {text}", file=sys.stderr)
        if not overwrite and os.path.exists(self.file_name):
            with open(self.file_name, 'r+b') as f:
                audio = f.read()
                f.close()
                return audio

        if voice_name is None:
            voice_name = GOOGLE_VOICES[lang]

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
        if self.file_name is not None:
            with open(self.file_name, 'wb') as f:
                f.write(response.audio_content)
                f.close()
                self.get_duration(from_file=True)

    def tts_azure_audio(self, text: str, lang: str, voice_name: str = None, speaking_rate: float = 1.0, overwrite: bool = False):

        if voice_name is None:
            voice_name = AZURE_VOICES[lang]

        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ['AZURE_API_KEY'],
            region="eastus",
        )
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
        # The language of the voice that speaks.
        # speech_config.speech_synthesis_voice_name = 'ar-EG-ShakirNeural'  # 'en-US-JennyNeural'

        audio_config = speechsdk.audio.AudioOutputConfig(filename=self.file_name)

        speech_synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speech_config,
            audio_config=audio_config
        )
        # speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        ssml = f"""
        <speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="en-US">
            <voice name="{voice_name}">
            <prosody rate="{speaking_rate}">
                {text}
            </prosody>
            </voice>
        </speak>"""
        # speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()
        speech_synthesis_result = speech_synthesizer.speak_ssml_async(ssml).get()

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"Speech synthesized for text [{text}]", file=sys.stderr)
            self.get_duration(from_file=True)

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: " + cancellation_details.error_details)
                    print("Did you set the speech resource key and region values?")