from .ui_dlg_export_subtitles import Ui_DlgExportSubtitles
from PyQt5 import QtWidgets
from dubbing_tools import Transcript, Timings
# from .mixins import DialogMixin
from PyQt5.QtWidgets import QDialog


class DlgExportSubtitles(QDialog, Ui_DlgExportSubtitles):

    transcript: Transcript
    lang: str = None
    timing: str = None
    sub_lang: str = None

    def __init__(self, transcript: Transcript):
        super().__init__()
        self.transcript = transcript
        self.setupUi(self)

        self.cmbLanguage.addItems(self.transcript.target_languages())
        self.cmbLanguage.activated.connect(self.language_selected)
        self.cmbTimingScheme.activated.connect(self.timing_selected)
        self.cmbSubtitleLanguage.activated.connect(self.sub_lang_selected)
        self.language_selected()

    def get_lang(self):
        return self.cmbLanguage.currentText()

    def get_timing_scheme(self):
        return self.cmbTimingScheme.currentText()

    def get_subtitle_lang(self):
        return self.cmbSubtitleLanguage.currentText()

    def language_selected(self):
        self.lang = self.cmbLanguage.currentText()
        self.cmbTimingScheme.clear()
        self.cmbTimingScheme.addItems(self.transcript.target_lang_timings(self.lang))
        self.timing_selected()

    def timing_selected(self):
        self.timing = self.cmbTimingScheme.currentText()
        self.cmbSubtitleLanguage.clear()
        self.cmbSubtitleLanguage.addItems([self.lang, self.transcript.src_lang])
        self.sub_lang_selected()

    def sub_lang_selected(self):
        self.sub_lang = self.cmbSubtitleLanguage.currentText()
        self.examine_state()

    def examine_state(self):
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(bool(self.sub_lang))
