from PyQt5.Qt import QObject
from PyQt5.QtCore import pyqtSignal
from subtitle import Subtitle


class SubtitleHandle(QObject):
    # define thread signals
    finished = pyqtSignal()
    display_subtitles = pyqtSignal()

    # error = pyqtSignal(QMessageBox.Icon, str)

    def __init__(self, video_id: str, parent):
        super(SubtitleHandle, self).__init__()

        # define parent and selected video
        self.parent_ = parent
        self.video_id = video_id
        self.success = False

    def get_subtitles(self):
        try:
            subtitle = Subtitle(self.video_id)
            self.parent_.current_video["subtitles_display"] = subtitle.get_subtitles()
            self.parent_.current_video["subtitle_object"] = subtitle
            self.success = True
        except Exception:
            self.parent_.current_video["subtitles_display"] = None

        self.finished.emit()
        self.display_subtitles.emit()
