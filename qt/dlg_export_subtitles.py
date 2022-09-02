from .ui_dlg_export_subtitles import Ui_DlgExportSubtitles
from PyQt5 import QtWidgets
from dubbing_tools import Transcript, Timings
from .mixins import DialogMixin


class DlgExportSubtitles(DialogMixin, Ui_DlgExportSubtitles):

    transcript: Transcript

    def __init__(self, transcript: Transcript):
        super().__init__()
        self.transcript = transcript

        self.cmbLanguage.addItems(self.transcript.target_languages())
        self.cmbTimingScheme.addItems(Timings.SCHEMES)
        self.cmbSubtitleLanguage.addItems([self.transcript.src_lang] + self.transcript.target_languages())

    def get_lang(self):
        return self.cmbLanguage.currentText()

    def get_timing_scheme(self):
        return self.cmbTimingScheme.currentText()

    def get_subtitle_lang(self):
        return self.cmbSubtitleLanguage.currentText()
