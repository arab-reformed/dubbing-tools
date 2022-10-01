import azure.cognitiveservices.speech as speechsdk
import re
import os
import sys
from typing import Optional
from .constants import *
from .audio import Audio


class AzureSpeechServices:

    speech_config: speechsdk.SpeechConfig
    audio_config: speechsdk.AudioConfig
    lang: str

    def __init__(self, lang):
        super().__init__()
        self.init_speech()
        self.lang = lang

    def init_speech(self):
        self.speech_config = speechsdk.SpeechConfig(
            subscription=os.environ['AZURE_API_KEY'],
            region="eastus",
        )
        self.speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )

    def tts_audio(self, audio: Audio, text: str, voice_name: str = None, speaking_rate: float = 1.0, overwrite: bool = False):

        if not overwrite and os.path.exists(audio.file_name):
            audio.get_duration()
            return

        if voice_name is None:
            voice_name = AZURE_VOICES[self.lang]

        if self.lang.split('-')[0] == 'ar':
            text = text.replace('«', '')
            text = text.replace('»', '')
            text = re.sub(r'^(.*)\s*-\s*$', '\\g<1>', text)
            text = re.sub(r'^\s*-\s*(.*)$', '\\g<1>', text)
            text = re.sub(r'(\d+):\s*(\d+)', '\\g<1> عَدَد \\g<2>', text)
            text = text.replace('\n', ' ')

        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ['AZURE_API_KEY'],
            region="eastus",
        )
        speech_config.set_speech_synthesis_output_format(
            speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
        )
        # The language of the voice that speaks.
        speech_config.speech_synthesis_voice_name = voice_name

        audio_config = speechsdk.audio.AudioOutputConfig(filename=audio.file_name)

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
        # speech_synthesis_result = speech_synthesizer.speak_text(text)
        speech_synthesis_result = speech_synthesizer.speak_ssml(ssml)

        if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print(f"{self.lang} {voice_name} synthesized [{text}] to {audio.file_name}", file=sys.stderr)
            audio.get_duration(from_file=True)

        elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = speech_synthesis_result.cancellation_details
            print(f"Speech synthesis canceled: {cancellation_details.reason}")
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                if cancellation_details.error_details:
                    print("Error details: " + cancellation_details.error_details)
                    print("Did you set the speech resource key and region values?")

    def speech_to_text(self, audio: Audio) -> Optional[str]:

        speech_config = speechsdk.SpeechConfig(
            subscription=os.environ['AZURE_API_KEY'],
            region="eastus",
        )
        speech_config.request_word_level_timestamps()

        audio_input = speechsdk.audio.AudioConfig(filename=audio.file_name)

        speech_recognizer = speechsdk.SpeechRecognizer(
            speech_config=speech_config,
            audio_config=audio_input,
        )

        result = speech_recognizer.recognize_once_async().get()

        if result.reason == speechsdk.ResultReason.RecognizedSpeech:
            # print("Recognized: {}".format(result.text), file=sys.stderr)
            return result.text

        elif result.reason == speechsdk.ResultReason.NoMatch:
            print("No speech could be recognized: {}".format(result.no_match_details), file=sys.stderr)

        elif result.reason == speechsdk.ResultReason.Canceled:
            cancellation_details = result.cancellation_details
            print("Speech Recognition canceled: {}".format(cancellation_details.reason), file=sys.stderr)
            if cancellation_details.reason == speechsdk.CancellationReason.Error:
                print("Error details: {}".format(cancellation_details.error_details), file=sys.stderr)
                print("Did you set the speech resource key and region values?", file=sys.stderr)

        return None
