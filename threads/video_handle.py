from PyQt5.Qt import QObject
from PyQt5.QtCore import pyqtSignal
from pytube import YouTube
from urllib.error import URLError
from http.client import IncompleteRead


class VideoHandle(QObject):
    # define thread signals
    finished = pyqtSignal()
    display_video_data = pyqtSignal()
    error = pyqtSignal(str, str)

    def __init__(self, video: YouTube, parent):
        super(VideoHandle, self).__init__()

        # define parent and selected video
        self.video = video
        self.parent_ = parent
        self.success = False

    def get_video_streams(self):
        try:
            streams = self.video.streams
            self.parent_.current_video["streams"] = streams
            self.success = True
        except (URLError, IncompleteRead):
            self.error.emit("critical", "Connection Error!")
        except Exception:
            self.error.emit("critical", "Unexpected Error!")

        self.finished.emit()
        if self.success:
            self.display_video_data.emit()
