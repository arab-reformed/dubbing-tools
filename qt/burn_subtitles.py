from PyQt5.QtCore import QObject, QThread, pyqtSignal
from dubbing_tools import Transcript
from dubbing_tools.functions import *
import ffmpeg
import asyncio


class Worker(QObject):
    finished = pyqtSignal(int)
    progress = pyqtSignal(str)
    log_line = pyqtSignal(str)

    transcript: Transcript
    lang: str
    timing_scheme: str
    sub_lang: str
    include_source: bool = False

    def __init__(self, transcript: Transcript, lang: str, timing_scheme: str, subtitle_lang: str, include_source: bool = False):
        super().__init__()
        self.transcript = transcript
        self.lang = lang
        self.timing_scheme = timing_scheme
        self.sub_lang = subtitle_lang
        self.include_source = include_source

    def run(self):
        self.transcript.export_subtitles(
            lang=self.lang,
            timing_scheme=self.timing_scheme,
            subtitle_lang=self.sub_lang,
            type='ass',
            include_source=self.include_source
        )

        mpeg = (
            ffmpeg.FFmpeg()
            .option('y')
            .input(video_fullpath(self.lang, self.timing_scheme))
            .output(
                subtitled_video_fullpath(self.lang, self.timing_scheme, self.sub_lang),
                acodec='copy',
                vcodec='libx264',
                vf=f"ass={subtitles_fullpath(self.lang, self.timing_scheme, self.sub_lang, 'ass')}",
                crf=20
            )
        )

        @mpeg.on('start')
        def on_start(arguments):
            pass
            # print('arguments:', arguments)

        @mpeg.on('stderr')
        def on_stderr(line: str):
            if not line.startswith('frame='):
                self.log_line.emit(line)

        @mpeg.on('progress')
        def on_progress(progress):
            self.progress.emit(f"Time: {progress.time}, speed: {progress.speed}")

        @mpeg.on('completed')
        def on_completed():
            pass
            # print('completed')

        @mpeg.on('terminated')
        def on_terminated():
            pass
            # print('terminated')

        @mpeg.on('error')
        def on_error(code):
            self.log_line.emit(f"ERROR: {code}")

        asyncio.run(mpeg.execute())

        self.finished.emit(1)
