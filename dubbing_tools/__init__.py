import os
# setup environment variable for FFMPEG.  Loading of moviepy with fail if the
# path cannot be found.
for path in ['/opt/homebrew/bin/ffmpeg']:
    if os.path.exists(path):
        os.environ['IMAGEIO_FFMPEG_EXE'] = path
        break

from .phrase import Phrase
from .transcript import Transcript
from .sourcelanguagePhrase import SourceLanguagePhrase
from .languagephrase import LanguagePhrase
from .phrasescontainer import PhrasesContainer
from .word import Word
from .audio import Audio
from .video import Video
from .timings import Timings
from .phrasetiming import PhraseTiming

__all__ = [
    'Audio',
    'LanguagePhrase',
    'Phrase',
    'PhrasesContainer',
    'PhraseTiming',
    'SourceLanguagePhrase',
    'Timings',
    'Transcript',
    'Video',
    'Word',
]
