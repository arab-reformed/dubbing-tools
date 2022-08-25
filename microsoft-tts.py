#!/usr/bin/env python3

import azure.cognitiveservices.speech as speechsdk
import fire


def cmd(text: str, mp3_file: str = None):
	speech_config = speechsdk.SpeechConfig(
		subscription="YourSubscriptionKey",
		region="YourServiceRegion",
	)
	speech_config.set_speech_synthesis_output_format(
		speechsdk.SpeechSynthesisOutputFormat.Audio16Khz32KBitRateMonoMp3
	)
	# The language of the voice that speaks.
	speech_config.speech_synthesis_voice_name='en-US-JennyNeural'

	if mp3_file is None:
		audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
	else:
		audio_config = speechsdk.audio.AudioOutputConfig(filename=mp3_file)

	speech_synthesizer = speechsdk.SpeechSynthesizer(
		speech_config=speech_config,
		audio_config=audio_config
	)
	# speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

	speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

	if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
		print(f"Speech synthesized for text [{text}]")

	elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
		cancellation_details = speech_synthesis_result.cancellation_details
		print(f"Speech synthesis canceled: {cancellation_details.reason}")
		if cancellation_details.reason == speechsdk.CancellationReason.Error:
			if cancellation_details.error_details:
				print("Error details: " + cancellation_details.error_details)
				print("Did you set the speech resource key and region values?")


if __name__ == "__main__":
    fire.Fire(cmd)
