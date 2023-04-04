from .ui_dlg_copy_lang import Ui_DlgCopyLanguage
from PyQt5 import QtWidgets
from dubbing_tools.transcript import Transcript


class DlgCopyLanguage(Ui_DlgCopyLanguage):

    dialog: QtWidgets.QDialog
    transcript: Transcript

    def __init__(self, transcript: Transcript):
        super().__init__()
        self.transcript = transcript
        self.dialog = QtWidgets.QDialog()
        self.setupUi(self.dialog)

    def setupUi(self, dialog: QtWidgets.QDialog):
        super().setupUi(dialog)
        self.cmbFromLanguage.addItems(self.transcript.target_languages())

    def exec_(self):
        return self.dialog.exec_()
