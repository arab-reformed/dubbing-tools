# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'qt/ui/dlg_delete_language.ui'
#
# Created by: PyQt5 UI code generator 5.15.6
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DlgDeleteLanguage(object):
    def setupUi(self, DlgDeleteLanguage):
        DlgDeleteLanguage.setObjectName("DlgDeleteLanguage")
        DlgDeleteLanguage.setWindowModality(QtCore.Qt.ApplicationModal)
        DlgDeleteLanguage.resize(274, 129)
        self.widget = QtWidgets.QWidget(DlgDeleteLanguage)
        self.widget.setGeometry(QtCore.QRect(30, 30, 211, 81))
        self.widget.setObjectName("widget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(self.widget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.cmbLanguage = QtWidgets.QComboBox(self.widget)
        self.cmbLanguage.setObjectName("cmbLanguage")
        self.horizontalLayout.addWidget(self.cmbLanguage)
        self.verticalLayout.addLayout(self.horizontalLayout)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.buttonBox = QtWidgets.QDialogButtonBox(self.widget)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(DlgDeleteLanguage)
        self.buttonBox.accepted.connect(DlgDeleteLanguage.accept) # type: ignore
        self.buttonBox.rejected.connect(DlgDeleteLanguage.reject) # type: ignore
        QtCore.QMetaObject.connectSlotsByName(DlgDeleteLanguage)

    def retranslateUi(self, DlgDeleteLanguage):
        _translate = QtCore.QCoreApplication.translate
        DlgDeleteLanguage.setWindowTitle(_translate("DlgDeleteLanguage", "Delete Language"))
        self.label.setText(_translate("DlgDeleteLanguage", "Language"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    DlgDeleteLanguage = QtWidgets.QDialog()
    ui = Ui_DlgDeleteLanguage()
    ui.setupUi(DlgDeleteLanguage)
    DlgDeleteLanguage.show()
    sys.exit(app.exec_())