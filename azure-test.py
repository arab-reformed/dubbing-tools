#!/usr/bin/env python3

from sys import flags, stderr
import fire
import dotenv
import azure.cognitiveservices.speech as speechsdk
import logging
import time
import os
import json
from dubbing_tools.word import Word

logging.basicConfig(
	stream=stderr,
	format='%(name)s %(levelname)s: %(message)s'
)
config = dotenv.load_dotenv()


def cmd(audio_file: str, output: str = None, debug: bool = False):
	logger = logging.getLogger('azure')
	if debug:
		logger.setLevel(logging.DEBUG)

	logger.debug(f"Speech to text for: {audio_file}")

    # speechapi_settings =  SpeechAPIConf()
	audio_filepath = audio_file
	locale = "en-US" # Change as per requirement

	audio_config = speechsdk.audio.AudioConfig(filename=audio_filepath) 
	speech_config = speechsdk.SpeechConfig(
		subscription=os.environ['AZURE_API_KEY'],
		region='eastus'
	)
	speech_config.request_word_level_timestamps()
	speech_config.speech_recognition_language = locale
	speech_config.output_format = speechsdk.OutputFormat(1)


	# Creates a recognizer with the given settings
	speech_recognizer = speechsdk.SpeechRecognizer(
		speech_config=speech_config,
		audio_config=audio_config
	)

	# Variable to monitor status
	done = False

	# Service callback for recognition text 
	results = []
	words = []  # list[Word]
	def parse_azure_result(evt):
		TICKS_PER_SECOND = 10000000
		response = json.loads(evt.result.json)
		results.append(response)
		for word in response['NBest'][0]['Words']:
			words.append(
				Word(
					id=len(words),
					word=word['Word'],
					start_time=word['Offset'] / TICKS_PER_SECOND,
					end_time=(word['Offset'] + word['Duration']) / TICKS_PER_SECOND
				)
			)
		logger.debug(evt)

	# Service callback that stops continuous recognition upon receiving an event `evt`
	def stop_cb(evt):
		logger.debug('CLOSING on {}'.format(evt))
		speech_recognizer.stop_continuous_recognition()
		nonlocal done
		done = True

		# Do something with the combined responses
		if output is not None:
			f = open(output, 'w')
			json.dump(results, f, indent=2)
			f.close()

			f = open('azure-words.json', 'w')
			json.dump(Word.schema().dump(words, many=True), f, indent=2)
			f.close()

	# Connect callbacks to the events fired by the speech recognizer
	speech_recognizer.recognizing.connect(lambda evt: logger.debug('RECOGNIZING: {}'.format(evt)))
	speech_recognizer.recognized.connect(parse_azure_result)
	speech_recognizer.session_started.connect(lambda evt: logger.debug('SESSION STARTED: {}'.format(evt)))
	speech_recognizer.session_stopped.connect(lambda evt: logger.debug('SESSION STOPPED {}'.format(evt)))
	speech_recognizer.canceled.connect(lambda evt: logger.debug('CANCELED {}'.format(evt)))
	# stop continuous recognition on either session stopped or canceled events
	speech_recognizer.session_stopped.connect(stop_cb)
	speech_recognizer.canceled.connect(stop_cb)

	# Start continuous speech recognition
	logger.debug("Initiating speech to text")
	speech_recognizer.start_continuous_recognition()
	while not done:
		time.sleep(.5)


if __name__ == "__main__":
    fire.Fire(cmd)
