from PyQt5.QtWidgets import QWidget, QComboBox
from PyQt5.uic import loadUi
from lib.load_piximage import load_piximage_from_url

# Other modules
from threading import Thread
from subtitle import Subtitle
from time_format import standard_time


class VideoTemplate(QWidget):
    def __init__(self, video: dict):
        super(VideoTemplate, self).__init__()
        self.video = video
        self.subtitle_object = None
        loadUi("./gui/video template", self)
        self.add_data()

    def add_data(self):
        self.title.setText(self.video["title"])
        self.length.setText(standard_time(self.video["length"]))
        self.get_subtitles.clicked.connect(self.display_subtitles)

    def generate_subtitles(self):
        try:
            self.subtitle_object = Subtitle(self.video["video_id"])
            combobox = self.findChild(QComboBox, "subtitles")
            for subtitle in self.subtitle_object.get_subtitles():
                combobox.addItem(subtitle)
        except Exception:
            pass

    def display_subtitles(self):
        self.grid_layout.removeWidget(self.get_subtitles)
        self.get_subtitles.deleteLater()
        combobox = QComboBox(self)
        combobox.addItem("no subtitle")
        combobox.setFixedHeight(35)
        combobox.setObjectName("subtitles")
        self.grid_layout.addWidget(combobox, 2, 7, 1, 2)
        Thread(target=self.generate_subtitles, daemon=False).start()

    def display_thumbnail(self):
        piximage = load_piximage_from_url(self.video["thumbnail"])
        img_label = self.img
        if piximage:
            img_label.setPixmap(piximage.scaledToWidth(130))
        else:
            img_label.setStyleSheet(img_label.styleSheet() + "color: #f32013;")
            img_label.setText("Failed!")
