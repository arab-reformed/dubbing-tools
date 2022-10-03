#!/usr/bin/env python3

import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog
from qt import *
from dubbing_tools import *
from PyQt5 import QtCore
import os


def window():
    QApplication.setApplicationName('Dubber')
    app = QApplication(sys.argv)
    print(app.applicationName())
    app.setApplicationName('Dubber')
    print(app.applicationName())
    mw = MainWindow(app.arguments())
    mw.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    window()
