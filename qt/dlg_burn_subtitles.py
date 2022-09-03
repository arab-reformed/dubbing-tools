from .ui_dlg_burn_subtitles import Ui_DlgBurnSubtitles
from PyQt5 import QtWidgets
from PyQt5.QtCore import QThread
import sys
import re
import fire
from dubbing_tools.functions import *
from dubbing_tools import *
import os
import ffmpeg
import asyncio
from .burn_subtitles import Worker


class DlgBurnSubtitles(QtWidgets.QDialog, Ui_DlgBurnSubtitles):

    transcript: Transcript
    lang: str
    timing_scheme: str
    sub_lang: str
    include_source: bool = False
    log: str = ''

    thread: QThread
    worker: Worker

    def __init__(self, parent, transcript: Transcript):  # , lang: str, timing_scheme: str, subtitle_lang: str, include_source: bool = False):
        super().__init__(parent=parent)
        self.transcript = transcript
        # self.lang = lang
        # self.timing_scheme = timing_scheme
        # self.sub_lang = subtitle_lang
        # self.include_source = include_source

        self.setupUi(self)

        self.cmbLanguage.addItems(self.transcript.target_languages())
        self.cmbLanguage.activated.connect(self.language_selected)
        self.cmbTimingScheme.activated.connect(self.timing_selected)
        self.cmbSubtitleLanguage.activated.connect(self.sub_lang_selected)
        self.language_selected()
        self.pbtBurnSubtitles.clicked.connect(self.burn_subtitles)
        self.pbtCancel.clicked.connect(self.close)

    def log_line(self, action: str):
        self.log += action + "\n"
        self.pteLog.setPlainText(self.log)

    def set_progress(self, progress: str):
        self.lneProgress.setText(progress)

    def language_selected(self):
        self.lang = self.cmbLanguage.currentText()
        self.cmbTimingScheme.clear()
        self.cmbTimingScheme.addItems(self.transcript.target_lang_timings(self.lang))
        self.timing_selected()

    def timing_selected(self):
        self.timing_scheme = self.cmbTimingScheme.currentText()
        self.cmbSubtitleLanguage.clear()
        self.cmbSubtitleLanguage.addItems([self.lang, self.transcript.src_lang])
        self.sub_lang_selected()

    def sub_lang_selected(self):
        self.sub_lang = self.cmbSubtitleLanguage.currentText()
        self.examine_state()

    def examine_state(self):
        self.pbtBurnSubtitles.setEnabled(bool(self.sub_lang))

    def cancel(self):
        self.close()

    def complete(self):
        QtWidgets.QMessageBox.information(
            parent=self,
            title='Burn Subtitles',
            text='Subtitles burned successfully'
        )
        self.close()

    def burn_subtitles(self):
        self.pbtBurnSubtitles.setEnabled(False)
        self.pbtCancel.setEnabled(False)

        self.thread = QThread()
        self.worker = Worker(self.transcript, self.lang, self.timing_scheme, self.sub_lang)

        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.finished.connect(self.complete)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.progress.connect(self.set_progress)
        self.worker.log_line.connect(self.log_line)

        self.thread.start()
