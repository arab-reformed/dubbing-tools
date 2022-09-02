from dubbing_tools import Transcript, Timings
from .ui_dlg_delete_language import Ui_DlgDeleteLanguage
from .mixins import DialogMixin


class DlgDeleteLanguage(DialogMixin, Ui_DlgDeleteLanguage):

    transcript: Transcript

    def __init__(self, transcript: Transcript):
        super().__init__()
        self.transcript = transcript

        self.cmbLanguage.addItems(self.transcript.target_languages())

    def get_lang(self):
        return self.cmbLanguage.currentText()
