import os
# setup environment variable for FFMPEG.  Loading of moviepy will fail if the
# path cannot be found.
for path in ['/opt/homebrew/bin/ffmpeg']:
    if os.path.exists(path):
        os.environ['IMAGEIO_FFMPEG_EXE'] = path
        break

__all__ = [
    'MINIMUM_GAP',
    'SUBTITLE_GAP',
]


MINIMUM_GAP = 0.3
SUBTITLE_GAP = 0.1
