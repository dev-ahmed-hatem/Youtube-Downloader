from http.client import IncompleteRead
from urllib.error import URLError
from os.path import basename, dirname, getsize
from time import sleep
from time_format import standard_time

# PyQt5 modules
from PyQt5.Qt import QThread, QWidget
from PyQt5.QtCore import pyqtSignal
from PyQt5.uic import loadUi
# Youtube modules
from pytube import YouTube, Playlist, Stream
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
            self.error.emit("critical", "Check your internet connection!", True, True)
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


class VideoDownloadHandleThread(QThread):
    on_download_start = pyqtSignal()
    on_download_finish = pyqtSignal()
    on_error = pyqtSignal()
    download_stat = pyqtSignal(dict)

    def __init__(self, stream: Stream, file_path: str, filesize: int):
        super(VideoDownloadHandleThread, self).__init__()
        self.stream = stream
        self.filename = basename(file_path)
        self.output_path = dirname(file_path)
        self.filesize = filesize
        self.analyzer = DownloadAnalyzerHandle(
            file=file_path,
            length=stream.filesize,
            callback=self.download_stat.emit
        )

        self.on_download_start.connect(self.analyzer.start)
        self.analyzer.finished.connect(self.stop)
        self.analyzer.finished.connect(self.deleteLater)

    def run(self) -> None:
        self.stream.download_state = True
        try:
            self.stream.download(
                output_path=self.output_path,
                filename=self.filename,
                start_signal=self.on_download_start,
                stop_signal=self.on_download_finish
            )
            self.finished.emit()
        except Exception:
            self.analyzer.terminate()
            self.on_error.emit()

    def stop(self):
        self.stream.download_state = False


class DownloadAnalyzerHandle(QThread):
    completed = pyqtSignal()

    def __init__(self, file: str, length: int, callback=None):
        super(DownloadAnalyzerHandle, self).__init__()
        self.filename = file
        self.length = length
        self.lastSize = 0
        self.callback = callback
        self.on_progress = True

        self.finished.connect(self.deleteLater)

    def run(self) -> None:
        delay = 0.2
        while self.on_progress:
            currentSize = getsize(self.filename)
            rate = (currentSize - self.lastSize) / delay
            estimatedSize = self.length - currentSize
            estimatedTime = standard_time(estimatedSize / rate) if rate else "N/A"
            self.lastSize = currentSize
            progress = int((currentSize / self.length) * 100)
            data = {
                "rate": rate,
                "downloaded": currentSize,
                "estimated_size": estimatedSize,
                "estimated_time": estimatedTime,
                "progress": progress
            }
            # print(data)
            if self.callback:
                self.callback(data)
            sleep(delay)
            if not progress < 100:
                self.completed.emit()
                break
        self.finished.emit()

    def stop(self):
        self.on_progress = False
