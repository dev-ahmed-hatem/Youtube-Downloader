from requests import get
from threading import Thread

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.uic import loadUi

from qt_material import apply_stylesheet
from pytube import YouTube, Playlist
from download_analyzer import DownloadAnalyzer
from subtitle import Subtitle


class CustomizingWindow(QDialog):
    playlist_custom_data = pyqtSignal(dict)

    def __init__(self, playlist_object: Playlist, parent=None):
        super(CustomizingWindow, self).__init__(parent)
        loadUi("./gui/playlist customizing window", self)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setWindowTitle(playlist_object.title)
        self.playlist = playlist_object
        self.playlist_data = {}
        self.videos_widgets = {}
        self.key_bindings()
        for video in playlist_object.videos:
            template = self.add_video(video)
            self.videos_area.addWidget(template)
            self.videos_widgets[video.title] = {"video": video, "template": template, "thumbnail": video.thumbnail_url}
        Thread(target=get_thumbnails, kwargs={"videos_widgets": self.videos_widgets}, daemon=True).start()

    def key_bindings(self):
        self.select_all.clicked.connect(lambda: self.toggle_select_all(self.select_all.isChecked()))
        self.videos.clicked.connect(lambda: self.change_type("video"))
        self.audios.clicked.connect(lambda: self.change_type("audio"))
        self.normal.clicked.connect(lambda: self.change_quality(0))
        self.low.clicked.connect(lambda: self.change_quality(1))
        self.default_button.clicked.connect(self.set_defaults)
        self.save_button.clicked.connect(self.fetch_playlist_data)

    def add_video(self, video: YouTube):
        template = QWidget()
        template.video_object = video
        loadUi("./gui/video template.ui", template)
        template.title.setText(video.title)
        template.length.setText(DownloadAnalyzer.standard_time(video.length))
        template.check.stateChanged.connect(self.check_selection)
        template.get_subtitles.clicked.connect(lambda: display_subtitles(template))
        return template

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

    def fetch_playlist_data(self):
        for video in self.videos_widgets:
            video_template = self.videos_widgets[video]["template"]
            subtitle_combobox = video_template.findChild(QComboBox, "subtitles")
            subtitle = 0
            if subtitle_combobox is not None:
                subtitle = subtitle_combobox.currentIndex()
            self.playlist_data[video] = {
                "include": video_template.check.isChecked(),
                "type": "video" if video_template.video_radio.isChecked() else "audio",
                "quality": "normal" if video_template.quality.currentIndex() == 0 else "low",
                "subtitle": "no subtitle"
                if subtitle == 0
                else video_template.subtitle_object.get_lang_code(subtitle - 1)
            }
        self.playlist_custom_data.emit(self.playlist_data)
        self.hide()


def load_piximage_from_url(url):
    try:
        image = QImage()
        image.loadFromData(get(url).content)
        return QPixmap(image).scaledToWidth(130)
    except Exception:
        return None


def get_thumbnails(videos_widgets: dict):
    for video in videos_widgets:
        piximage = load_piximage_from_url(videos_widgets[video]["thumbnail"])
        img_label = videos_widgets[video]["template"].img
        if piximage:
            img_label.setPixmap(piximage)
        else:
            img_label.setStyleSheet(img_label.styleSheet() + "color: #f32013;")
            img_label.setText("Failed!")


def generate_subtitles(template: QWidget):
    try:
        template.subtitle_object = Subtitle(template.video_object.video_id)
        combobox = template.findChild(QComboBox, "subtitles")
        for subtitle in template.subtitle_object.get_subtitles():
            combobox.addItem(subtitle)
    except Exception:
        pass


def display_subtitles(template: QWidget):
    template.grid_layout.removeWidget(template.get_subtitles)
    template.get_subtitles.deleteLater()
    combobox = QComboBox(template)
    combobox.addItem("no subtitle")
    combobox.setFixedHeight(35)
    combobox.setObjectName("subtitles")
    template.grid_layout.addWidget(combobox, 2, 7, 1, 2)
    Thread(target=generate_subtitles, kwargs={"template": template}, daemon=False).start()

