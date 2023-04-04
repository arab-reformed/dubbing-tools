from dubbing_tools.transcript import Transcript
from .ui_dlg_delete_language import Ui_DlgDeleteLanguage
from .mixins import DialogMixin
from PyQt5.QtWidgets import QDialog, QDialogButtonBox


class DlgDeleteLanguage(QDialog, Ui_DlgDeleteLanguage):

    transcript: Transcript
    lang: str = None

    def __init__(self, transcript: Transcript):
        super().__init__()
        self.transcript = transcript
        self.setupUi(self)

        self.cmbLanguage.addItems(self.transcript.target_languages())
        self.cmbLanguage.setCurrentIndex(-1)
        self.cmbLanguage.activated.connect(self.lang_selected)
        self.examine_state()

    def get_lang(self):
        return self.cmbLanguage.currentText()

    def lang_selected(self, index: int):
        print('index:', index)
        self.lang = self.cmbLanguage.currentText()
        self.examine_state()

    def examine_state(self):
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(bool(self.lang))
