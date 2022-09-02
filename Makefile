all: qt/ui_mainwindow.py \
	qt/ui_copy_lang.py \
	qt/ui_dlg_export_subtitles.py \
	qt/ui_dlg_delete_language.py

qt/ui_%.py: qt/ui/%.ui
	pyuic5 -x $< -o $@
