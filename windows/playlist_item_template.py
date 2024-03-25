from PyQt5.QtWidgets import QWidget
from PyQt5uic import loadUi


class PlaylistItemTemplate(QWidget):
    def __init__(self, video_data: dict, order: int):
        super(PlaylistItemTemplate, self).__init__()
        loadUi("./gui/playlist item template", self)
        self.video_data = video_data
        self.order = order
        self.dislay_data()

    def dislay_data(self):
        self.title.setText(self.video_data["title"])
        self.index.setText(str(self.order))
