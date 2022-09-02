from PyQt5 import QtWidgets


class DialogMixin:

    dialog: QtWidgets.QDialog

    def __init__(self):
        super().__init__()
        self.dialog = QtWidgets.QDialog()
        self.setupUi(self.dialog)

    def setupUi(self, dialog: QtWidgets.QDialog):
        super().setupUi(dialog)

    def exec_(self):
        return self.dialog.exec_()
