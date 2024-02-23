from PyQt5.QtWidgets import QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5.QtGui import QCloseEvent

from load_piximage import load_piximage_from_url
from threading import Thread
from pytube import Stream

from threads.object_handle import VideoDownloadHandleThread

from filesize import naturalsize
from os.path import basename, dirname
from os import startfile


class VideoDownloadWindow(QMainWindow):
    def __init__(self, parent, download_data: dict):
        super(VideoDownloadWindow, self).__init__()
        loadUi("./gui/video download", self)
        self.download_data = download_data
        self.display_data()
        self.key_bindings()
        self.setWindowTitle(download_data["title"])
        self.main_window = parent

        # declare the current manipulated stream
        self.download_handle = None
        self.tasks = {}
        self.current_task = 0
        self.pause = False

    def key_bindings(self):
        self.pause_resume_btn.clicked.connect(self.pause_resume)
        self.cancel_btn.clicked.connect(self.close)

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
            self.img_1.setStyleSheet(self.img_1.styleSheet() + "color: #f32013;")
            self.img_2.setStyleSheet(self.img_2.styleSheet() + "color: #f32013;")
            self.img_1.setText("Failed!")
            self.img_2.setText("Failed!")

    def display_download_stat(self, stat: dict):
        self.rate.setText(f"{naturalsize(stat['rate'])}/s")
        self.downloaded.setText(str(naturalsize(stat["downloaded"])))
        self.estimated.setText(f"Size: {naturalsize(stat['estimated_size'])}      Time: {stat['estimated_time']}")
        self.progress.setValue(stat["progress"])
        self.progress_label.setText(f"Progress:    {stat['progress']}%")

    def manage_tasks(self):
        stream_type = self.download_data["stream_type"]
        if stream_type == "video" or stream_type == "audio":
            self.download_stream(stream=self.download_data[f"{stream_type}_stream_object"],
                                 file_path=self.download_data["location"],
                                 stream_type=f"{stream_type}")

    def download_stream(self, stream: Stream, file_path, stream_type: str):
        self.download_handle = VideoDownloadHandleThread(
            stream=stream,
            file_path=file_path,
            filesize=stream.filesize
        )
        self.download_handle.download_stat.connect(self.display_download_stat)
        self.download_handle.analyzer.completed.connect(self.on_download_finished)
        self.download_handle.on_error.connect(self.on_error)
        self.download_handle.finished.connect(lambda: print("finished"))
        self.download_handle.start()
        self.statusBar().showMessage(f"downloading {stream_type} ..")

    def pause_resume(self):
        if self.pause:
            self.pause = False
            self.manage_tasks()
            self.pause_resume_btn.setText("Pause")
        else:
            self.pause = True
            self.download_handle.analyzer.stop()
            self.download_handle.terminate()
            self.download_handle.wait()
            self.pause_resume_btn.setText("Resume")
            self.statusBar().showMessage("download paused")

    def closeEvent(self, a0: QCloseEvent) -> None:
        if not self.pause:
            self.pause_resume()
        a0.accept()

    def on_download_finished(self):
        file_path = self.download_data['location']
        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Download Finished")
        msg.setIcon(QMessageBox.Information)
        msg.setText(basename(file_path))
        msg.addButton("open", QMessageBox.AcceptRole)
        msg.addButton("open folder", QMessageBox.AcceptRole)
        msg.addButton("download another", QMessageBox.AcceptRole)
        msg.addButton("exit", QMessageBox.AcceptRole)
        btn = msg.exec()

        if btn == 0:
            startfile(file_path)
        elif btn == 1:
            startfile(dirname(file_path))
        elif btn == 2:
            self.prepare_another()
            return
        exit()

    def on_error(self):
        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Error!")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Error happened while downloading {self.download_data['title']}")
        msg.addButton("Try again", QMessageBox.AcceptRole)
        msg.addButton("Exit", QMessageBox.AcceptRole)
        btn = msg.exec()

        if btn == 0:
            self.manage_tasks()
        else:
            exit()

    def prepare_another(self):
        self.hide()
        self.main_window.reset_gui()
        self.main_window.show()
