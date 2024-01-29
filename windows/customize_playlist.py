from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget, QComboBox
from PyQt5.uic import loadUi

from threading import Thread


class CustomizingWindow(QDialog):
    playlist_custom_data = pyqtSignal(dict)

    def __init__(self, playlist_title: str, videos_widgets: dict, parent=None):
        super(CustomizingWindow, self).__init__(parent)
        loadUi("./gui/playlist customizing window", self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(playlist_title)
        self.videos_widgets = videos_widgets
        self.key_bindings()
        for video in self.videos_widgets:
            template = self.videos_widgets[video]["template"]
            template.check.stateChanged.connect(self.check_selection)
            self.videos_area.addWidget(template)
        Thread(target=self.load_thumbnails, daemon=True).start()

    def key_bindings(self):
        self.select_all.clicked.connect(lambda: self.toggle_select_all(self.select_all.isChecked()))
        self.videos.clicked.connect(lambda: self.change_type("video"))
        self.audios.clicked.connect(lambda: self.change_type("audio"))
        self.normal.clicked.connect(lambda: self.change_quality(0))
        self.low.clicked.connect(lambda: self.change_quality(1))
        self.default_button.clicked.connect(self.set_defaults)
        self.save_button.clicked.connect(self.fetch_playlist_data)

    @staticmethod
    def load_saved_changes(template: QWidget, customized_data: dict):
        template.check.setChecked(customized_data["include"])
        if customized_data["type"] == "video":
            template.video_radio.setChecked(True)
            template.audio_radio.setChecked(False)
        else:
            template.video_radio.setChecked(False)
            template.audio_radio.setChecked(True)
        template.quality.setCurrentIndex(0 if customized_data["quality"] == "normal" else 1)
        subtitle_combobox = template.findChild(QComboBox, "subtitles")
        if customized_data["subtitle"] == "no subtitle":
            if subtitle_combobox:
                subtitle_combobox.setCurrentIndex(0)
        else:
            subtitle_combobox.setCurrentIndex(customized_data["subtitle_index"])

    def set_defaults(self):
        self.select_all.setChecked(True)
        self.toggle_select_all(1)
        self.change_type("video")
        self.change_quality(0)
        for video in self.videos_widgets:
            if self.videos_widgets[video]["template"].findChild(QComboBox, "subtitles"):
                self.videos_widgets[video]["template"].findChild(QComboBox, "subtitles").setCurrentIndex(0)

    def toggle_select_all(self, state):
        for video in self.videos_widgets:
            self.videos_widgets[video]["template"].check.setChecked(bool(state))

    def change_type(self, stream_type):
        for video in self.videos_widgets:
            self.videos_widgets[video]["template"].video_radio.setChecked(True if stream_type == "video" else False)
            self.videos_widgets[video]["template"].audio_radio.setChecked(True if stream_type == "audio" else False)

    def change_quality(self, quality):
        for video in self.videos_widgets:
            self.videos_widgets[video]["template"].quality.setCurrentIndex(quality)

    def check_selection(self):
        selected = 0
        for video in self.videos_widgets:
            selected += 1 if self.videos_widgets[video]["template"].check.isChecked() else 0
        self.select_all.setChecked(selected == len(self.videos_widgets.keys()))
        self.save_button.setEnabled(bool(selected))

    def load_thumbnails(self):
        for video in self.videos_widgets:
            self.videos_widgets[video]["template"].display_thumbnail()

    def fetch_playlist_data(self):
        for video in self.videos_widgets:
            video_template = self.videos_widgets[video]["template"]
            subtitle_combobox = video_template.findChild(QComboBox, "subtitles")
            subtitle = 0
            if subtitle_combobox is not None:
                subtitle = subtitle_combobox.currentIndex()
            self.videos_widgets[video]["customized_data"] = {
                "include": video_template.check.isChecked(),
                "type": "video" if video_template.video_radio.isChecked() else "audio",
                "quality": "normal" if video_template.quality.currentIndex() == 0 else "low",
                "subtitle": "no subtitle"
                if subtitle == 0
                else video_template.subtitle_object.get_lang_code(subtitle - 1),
                "subtitle_index": subtitle
            }
        self.playlist_custom_data.emit(self.videos_widgets)
        self.hide()
