#!/usr/bin/env python3

import json
import fire
from typing import List
from classes import *
import dotenv
from jinja2 import Environment, PackageLoader, select_autoescape, TemplateNotFound, Template
from dotted_dict import DottedDict
import sys

dotenv.load_dotenv()


def cmd(transcript_file: str, lang: str):
    container = Transcript.load_file(transcript_file)
    phrases = []
    for i, phrase in enumerate(container.phrases):
        data = DottedDict()
        data.id = phrase.id
        data.source = phrase.source
        data.target = phrase.get_target(lang)
        data.ratio = round(data.target.natural_duration / data.source.duration(), 2)
        if i < container.phrase_count()-1:
            data.gap_between = phrase.source.gap_between(container.phrases[i+1].source)
        phrases.append(data)

    env = Environment(
        loader=PackageLoader("duration-stats"),
        autoescape=select_autoescape()
    )

    try:
        template = env.get_template('duration-stats.html')
    except TemplateNotFound as e:
        print('Template file not found: ' + str(e), file=sys.stderr)
        exit(1)

    print(template.render(phrases=phrases))


if __name__ == "__main__":
    fire.Fire(cmd)
