from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from dubbing_tools.transcript import Transcript
from dubbing_tools.functions import *
import ffmpeg
import asyncio


class Worker(QObject):
    finished = pyqtSignal(int)
    terminated = pyqtSignal(int)
    progress = pyqtSignal(str)
    log_line = pyqtSignal(str)

    transcript: Transcript
    lang: str
    timing_scheme: str
    sub_lang: str
    include_source: bool = False

    mpeg = None
    mpeg_terminated: bool = False
    please_terminate: bool = False

    def __init__(self, transcript: Transcript, lang: str, timing_scheme: str, subtitle_lang: str, include_source: bool = False):
        super().__init__()
        self.transcript = transcript
        self.lang = lang
        self.timing_scheme = timing_scheme
        self.sub_lang = subtitle_lang
        self.include_source = include_source

    # @pyqtSlot(int)
    def terminate(self, signal: int):
        print(f'Received termination signal: {signal}.')
        if not self.mpeg_terminated:
            self.mpeg.terminate()
            self.mpeg_terminated = True

    def run(self):
        self.transcript.export_subtitles(
            audio_lang=self.lang,
            timing_scheme=self.timing_scheme,
            subtitle_lang=self.sub_lang,
            sub_type='ass',
            include_source=self.include_source
        )

        self.mpeg = (
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

        @self.mpeg.on('start')
        def on_start(arguments):
            pass
            # print('arguments:', arguments)

        @self.mpeg.on('stderr')
        def on_stderr(line: str):
            if not line.startswith('frame='):
                self.log_line.emit(line)

        @self.mpeg.on('progress')
        def on_progress(progress):
            if self.please_terminate:
                self.terminate(2)
            self.progress.emit(f"Time: {progress.time}, speed: {progress.speed}")

        @self.mpeg.on('completed')
        def on_completed():
            pass
            # print('completed')

        @self.mpeg.on('terminated')
        def on_terminated():
            pass
            # print('terminated')

        @self.mpeg.on('error')
        def on_error(code):
            self.log_line.emit(f"ERROR: {code}")

        asyncio.run(self.mpeg.execute())
        # self.mpeg.execute()

        if self.mpeg_terminated:
            print('terminated signal sent')
            self.terminated.emit(1)
        else:
            print('finished signal sent')
            self.finished.emit(1)
