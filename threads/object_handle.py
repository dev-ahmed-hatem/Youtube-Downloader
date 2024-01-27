# PyQt5 modules
from PyQt5.Qt import QObject
from PyQt5.QtCore import pyqtSignal

# Youtube modules
from pytube import YouTube, Playlist
from urllib.error import URLError
from http.client import IncompleteRead

# Subtitle modules
from subtitle import Subtitle


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


class PlaylistHandle(QObject):
    # define thread signals
    display_playlist_data = pyqtSignal()
    display_playlist_size = pyqtSignal()
    finished = pyqtSignal()
    error = pyqtSignal(str, str, bool, bool)

    def __init__(self, playlist_url, parent):
        super(PlaylistHandle, self).__init__()

        self.parent_ = parent
        self.playlist_url = playlist_url
        self.success = False
        self.pass_ = True

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

        self.finished.emit()
        if self.success:
            self.display_playlist_data.emit()

    def calculate_size_data(self):
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

        self.finished.emit()
        if self.success:
            self.display_playlist_size.emit()
        else:
            self.parent_.approx_size.setText("Unknown")
