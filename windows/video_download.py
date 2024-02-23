from PyQt5.QtWidgets import QMainWindow
from PyQt5.uic import loadUi
from PyQt5.QtGui import QShowEvent

from lib.load_piximage import load_piximage_from_url
from threading import Thread
from pytube import Stream

from threads.object_handle import VideoDownloadHandleThread

from filesize import naturalsize


class VideoDownloadWindow(QMainWindow):
    def __init__(self, download_data: dict):
        super(VideoDownloadWindow, self).__init__()
        loadUi("./gui/video download", self)
        self.download_data = download_data
        self.display_data()
        self.key_bindings()

        # declare the current manipulated stream
        self.download_handle = None
        self.tasks = {}
        self.current_task = 0

    def key_bindings(self):
        self.pause_resume_btn.clicked.connect(self.pause_resume)

    def display_data(self):
        # displaying video details
        self.title.setText(self.download_data["title"])
        self.author.setText(self.download_data["author"])
        self.length.setText(self.download_data["length"])
        self.quality.setText(self.download_data["quality"])
        self.size.setText(self.download_data["size"])
        self.url.setText(self.download_data["url"])
        self.location.setText(self.download_data["location"])
        Thread(target=self.display_thumbnail, daemon=True).start()

    def display_thumbnail(self):
        piximage = load_piximage_from_url(self.download_data["thumbnail"])
        if piximage:
            self.img_1.setPixmap(piximage.scaledToWidth(243))
            self.img_2.setPixmap(piximage.scaledToWidth(243))
        else:
            self.img_1.setStyleSheet(img_label.styleSheet() + "color: #f32013;")
            self.img_2.setStyleSheet(img_label.styleSheet() + "color: #f32013;")
            self.img_1.setText("Failed!")
            self.img_2.setText("Failed!")

    def display_download_stat(self, stat: dict):
        self.rate.setText(f"{naturalsize(stat['rate'])}/s")
        self.downloaded.setText(str(naturalsize(stat["downloaded"])))
        self.estimated.setText(f"Size: {naturalsize(stat['estimated_size'])}      Time: {stat['estimated_time']}")
        self.progress.setValue(stat["progress"])
        self.progress_label.setText(f"Progress: {stat['progress']}%")

    def manage_tasks(self):
        if self.download_data["stream_type"] == "progressive":
            self.download_stream(stream=self.download_data["video_stream_object"],
                                 file_path=self.download_data["location"])

    def download_stream(self, stream: Stream, file_path):
        self.download_handle = VideoDownloadHandleThread(
            stream=stream,
            file_path=file_path,
            filesize=stream.filesize
        )
        self.download_handle.download_stat.connect(self.display_download_stat)
        self.download_handle.finished.connect(lambda: print("finished"))
        print(file_path)
        self.download_handle.start()
        # return

    def pause_resume(self):
        self.download_handle.analyzer.stop()
