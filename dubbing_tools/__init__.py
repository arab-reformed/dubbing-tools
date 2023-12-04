import os
import re
# setup environment variable for FFMPEG.  Loading of moviepy will fail if the
# path cannot be found.
for path in ['/opt/homebrew/bin/ffmpeg']:
    if os.path.exists(path):
        os.environ['IMAGEIO_FFMPEG_EXE'] = path
        break

__all__ = [
    'strip_text',
    'MINIMUM_GAP',
    'SUBTITLE_GAP',
]


MINIMUM_GAP = 0.3
SUBTITLE_GAP = 0.1

def strip_text(text: str) -> str:
    return re.sub(r'[,.;:]', '', text).strip()
