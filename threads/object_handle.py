# PyQt5 modules
from http.client import IncompleteRead
from urllib.error import URLError

from PyQt5.Qt import QThread, QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
# Youtube modules
from pytube import YouTube, Playlist
# Subtitle modules
from subtitle import Subtitle


class VideoHandleThread(QThread):
    # define thread signals
    display_video_data = pyqtSignal()
    error = pyqtSignal(str, str)

    def __init__(self, video: YouTube, parent):
        super(VideoHandleThread, self).__init__()

        # define parent and selected video
        self.video = video
        self.parent_ = parent
        self.success = False

    def run(self):
        try:
            streams = self.video.streams
            self.parent_.current_video["streams"] = streams
            self.success = True
        except (URLError, IncompleteRead):
            self.error.emit("critical", "Connection Error!")
        except Exception:
            self.error.emit("critical", "Unexpected Error!")

        if self.success:
            self.display_video_data.emit()
        self.finished.emit()


class SubtitleHandleThread(QThread):
    # define thread signals
    display_subtitles = pyqtSignal()

    # error = pyqtSignal(QMessageBox.Icon, str)

    def __init__(self, video_id: str, parent):
        super(SubtitleHandleThread, self).__init__()

        # define parent and selected video
        self.parent_ = parent
        self.video_id = video_id
        self.success = False

    def run(self):
        try:
            subtitle = Subtitle(self.video_id)
            self.parent_.current_video["subtitles_display"] = subtitle.get_subtitles()
            self.parent_.current_video["subtitle_object"] = subtitle
            self.success = True
        except Exception:
            self.parent_.current_video["subtitles_display"] = None

        self.display_subtitles.emit()
        self.finished.emit()


class PlaylistHandleThread(QThread):
    # define thread signals
    display_playlist_data = pyqtSignal()
    display_playlist_size = pyqtSignal()
    error = pyqtSignal(str, str, bool, bool)

    def __init__(self, playlist_url, parent):
        super(PlaylistHandleThread, self).__init__()

        self.parent_ = parent
        self.playlist_url = playlist_url
        self.success = False
        self.handle_size = False

    def run(self) -> None:
        self.success = False
        if self.handle_size:
            self.get_size_data()
        else:
            self.get_playlist_data()
        self.finished.emit()

    def get_playlist_data(self):
        try:
            playlist = Playlist(self.playlist_url)
            title = playlist.title
            count = len(list(playlist.videos))
            self.parent_.current_playlist["playlist"] = playlist
            self.parent_.current_playlist["playlist_title"] = title
            self.parent_.current_playlist["playlist_count"] = count
            self.success = True

        except KeyError:
            self.error.emit("critical", "Invalid URL!", True, True)
        except URLError:
            self.error.emit("critical", "Connection Error!", True, True)
        except Exception:
            self.error.emit("critical", "Unexpected Error!", True, True)

        if self.success:
            self.display_playlist_data.emit()

    def get_size_data(self):
        try:
            first_vid = self.parent_.current_playlist["playlist"].videos[0]
            length = first_vid.length
            streams = first_vid.streams
            progressive = streams.filter(progressive=True)
            audio = streams.filter(only_audio=True)
            qualities = {"progressive": len(progressive),
                         "audio": len(audio)
                         }
            mul_factor = {"normal progressive": progressive[-1].filesize / length,
                          "low progressive": progressive[-2].filesize / length if qualities["progressive"] > 1 else 0,
                          "normal audio": audio[-1].filesize / length,
                          "low audio": audio[-2].filesize / length if qualities["audio"] > 1 else 0
                          }
            durations = [video.length for video in self.parent_.current_playlist["playlist"].videos]
            self.parent_.current_playlist["size"] = True
            self.parent_.current_playlist["playlist_mul_factor"] = mul_factor
            self.parent_.current_playlist["playlist_videos_durations"] = durations
            self.success = True

        except KeyError:
            self.error.emit("critical", "Invalid URL!\nCouldn't calculate size", False, True)
        except URLError:
            self.error.emit("critical", "Connection Error!\nCouldn't calculate size", False, True)
        except Exception:
            self.error.emit("critical", "Unexpected Error!\nCouldn't calculate size", False, True)

        if self.success:
            self.display_playlist_size.emit()
        else:
            self.parent_.approx_size.setText("Unknown")


class CustomizingHandleThread(QThread):
    def __init__(self, playlist, parent):
        super(CustomizingHandleThread, self).__init__()
        self.parent_ = parent
        self.playlist_object = playlist
        self.videos_widgets = {}

    def run(self) -> None:
        for video in self.playlist_object.videos:
            self.videos_widgets[video.title] = {"video": video,
                                                "video_data": {
                                                    "video_id": video.video_id,
                                                    "title": video.title,
                                                    "length": video.length,
                                                    "thumbnail": video.thumbnail_url
                                                }}
        self.parent_.current_playlist["download_data"] = self.videos_widgets
        self.finished.emit()
