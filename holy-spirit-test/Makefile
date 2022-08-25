
all: phrases.json

words.json: manuscript.txt ../functions.py ../manuscript-to-words.py
	python3 ../manuscript-to-words.py transcript.json manuscript.txt > words.json

phrases.json: words.json ../functions.py ../words-to-phrases.py
	python3 ../words-to-phrases.py words.json > phrases.json
