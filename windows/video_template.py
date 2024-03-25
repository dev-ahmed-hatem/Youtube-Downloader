from PyQt5.QtWidgets import QWidget, QComboBox
from PyQt5uic import loadUi
from lib.load_piximage import load_piximage_from_url

# Other modules
from threading import Thread
from lib.subtitle import Subtitle
from lib.time_format import standard_time


class VideoTemplate(QWidget):
    def __init__(self, video: dict):
        super(VideoTemplate, self).__init__()
        self.video = video
        self.subtitle_object = None
        loadUi("./gui/video template", self)
        self.display_data()

    def display_data(self):
        self.title.setText(self.video["title"])
        self.length.setText(self.video["length"])
        self.get_subtitles.clicked.connect(self.display_subtitles)

    def generate_subtitles(self):
        try:
            self.video["subtitle"] = Subtitle(self.video["video_id"])
            combobox = self.findChild(QComboBox, "subtitles")
            for subtitle in self.video["subtitle"].get_subtitles():
                combobox.addItem(subtitle)
        except Exception as e:
            print(e)

    def display_subtitles(self):
        self.grid_layout.removeWidget(self.get_subtitles)
        self.get_subtitles.deleteLater()
        combobox = QComboBox(self)
        combobox.addItem("no subtitle")
        combobox.setFixedHeight(35)
        combobox.setObjectName("subtitles")
        self.grid_layout.addWidget(combobox, 2, 7, 1, 2)
        Thread(target=self.generate_subtitles, daemon=False).start()
