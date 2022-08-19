#!/usr/bin/env python3

import json
import fire


def cmd(words_file: str):
    with open(words_file, 'r') as f:
        words = json.load(f)

    stats = {}

    for i, word in enumerate(words):
        if i < len(words)-1:
            gap = str(round(words[i+1]['start_time'] - word['end_time'], 2))
            if gap in stats:
                stats[gap] += 1
            else:
                stats[gap] = 1

    import pprint
    pprint.pprint(stats)


if __name__ == "__main__":
    fire.Fire(cmd)
