import json
import fire
from functions import get_phrases


def cmd(words_file: str):
    with open(words_file, 'r') as f:
        words = json.load(f)

    phrases = get_phrases(words, 'en')

    print(json.dumps(phrases, indent=2))


if __name__ == "__main__":
    fire.Fire(cmd)
