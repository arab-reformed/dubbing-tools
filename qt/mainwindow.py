import sys
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWidgets import QFileDialog
from .ui_mainwindow import Ui_WindowMain
from .copy_lang import DlgCopyLanguage
from .dlg_export_subtitles import DlgExportSubtitles
from .dlg_delete_language import DlgDeleteLanguage
from dubbing_tools import *
from PyQt5 import QtCore
import os


class MainWindow(Ui_WindowMain):
    window: QMainWindow
    transcript: Transcript
    transcript_path: str

    def __init__(self, args: list[str]):
        super().__init__()
        self.window = QMainWindow()
        print('Arguments:', args)
        self.setupUi(self.window)
        if len(args) > 1:
            self.load_transcript(args[1])

    def setupUi(self, main_window):
        super().setupUi(main_window)
        self.pbSelectProject.clicked.connect(self.load_project)
        self.actionOpenProject.triggered.connect(self.load_project)
        self.actionCopyLanguage.triggered.connect(self.copy_language)
        self.actionExportSubtitles.triggered.connect(self.export_subtitles)
        self.actionDeleteLanguage.triggered.connect(self.delete_language)
        self.actionQuit.triggered.connect(self.quit)

    def load_transcript(self, path: str):
        self.transcript = Transcript.load(path)
        if self.transcript is not None:
            self.transcript_path = path
            self.lneProjectPath.setText(path)
            self.set_languages(self.transcript.target_languages())
        else:
            self.transcript_path = ''

    def show(self):
        return self.window.show()

    def load_project(self):
        dialog = QFileDialog(caption='Open Project', directory=os.getcwd())
        dialog.setFileMode(QFileDialog.Directory)
        if dialog.exec_():
            self.load_transcript(dialog.selectedFiles()[0])

    def save_project(self):
        if self.transcript.has_changed:
            self.transcript.save()

    def export_subtitles(self):
        dialog = DlgExportSubtitles(self.transcript)
        if dialog.exec_():
            lang = dialog.get_lang()
            timing_scheme = dialog.get_timing_scheme()
            sub_lang = dialog.get_subtitle_lang()

            if lang and timing_scheme and sub_lang \
                    and self.transcript.phrases[0].get_timing(lang, timing_scheme) \
                    and sub_lang in self.transcript.target_languages() or sub_lang == self.transcript.src_lang:

                self.transcript.export_subtitles(
                    lang=lang,
                    timing_scheme=timing_scheme,
                    subtitle_lang=sub_lang,
                    type='ass',
                )

    def copy_language(self):
        dialog = DlgCopyLanguage(self.transcript)
        if dialog.exec_():
            from_lang = dialog.cmbFromLanguage.currentText()
            to_lang = dialog.lneToLanguage.text()

            if from_lang and to_lang and from_lang != to_lang and to_lang not in self.transcript.target_languages():
                self.transcript.copy_target(from_lang=from_lang, to_lang=to_lang)

    def delete_language(self):
        dialog = DlgDeleteLanguage(self.transcript)
        if dialog.exec_():
            self.transcript.delete_target(dialog.get_lang())

    def set_languages(self, langs: list[str]):
        self.leLanguagesList.setText(', '.join(langs))

    def quit(self):
        if self.transcript.has_changed:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Question)
            msg.setText("Save the project?")
            msg.setInformativeText("If changes are not saved they will be lost.")
            msg.setWindowTitle("Save Changes?")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

            retval = msg.exec_()
            if retval == QMessageBox.Yes:
                self.save_project()

        QCoreApplication.quit()
