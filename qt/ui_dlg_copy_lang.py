# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/ui/dlg_copy_lang.ui'
#
# Created by: PyQt5 UI code generator 5.15.7
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DlgCopyLanguage(object):
    def setupUi(self, DlgCopyLanguage):
        DlgCopyLanguage.setObjectName("DlgCopyLanguage")
        DlgCopyLanguage.resize(230, 121)
        self.verticalLayout = QtWidgets.QVBoxLayout(DlgCopyLanguage)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(DlgCopyLanguage)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.cmbFromLanguage = QtWidgets.QComboBox(DlgCopyLanguage)
        self.cmbFromLanguage.setObjectName("cmbFromLanguage")
        self.gridLayout.addWidget(self.cmbFromLanguage, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(DlgCopyLanguage)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        self.lneToLanguage = QtWidgets.QLineEdit(DlgCopyLanguage)
        self.lneToLanguage.setObjectName("lneToLanguage")
        self.gridLayout.addWidget(self.lneToLanguage, 1, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(DlgCopyLanguage)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgCopyLanguage)
        self.buttonBox.accepted.connect(DlgCopyLanguage.accept) # type: ignore
        self.buttonBox.rejected.connect(DlgCopyLanguage.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(DlgCopyLanguage)

    def retranslateUi(self, DlgCopyLanguage):
        _translate = QtCore.QCoreApplication.translate
        DlgCopyLanguage.setWindowTitle(_translate("DlgCopyLanguage", "Copy Language"))
        self.label.setText(_translate("DlgCopyLanguage", "Copy from:"))
        self.label_2.setText(_translate("DlgCopyLanguage", "Copy to:"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DlgCopyLanguage = QtWidgets.QDialog()
    ui = Ui_DlgCopyLanguage()
    ui.setupUi(DlgCopyLanguage)
    DlgCopyLanguage.show()
    sys.exit(app.exec_())