from PyQt5.QtWidgets import QMainWindow, QMessageBox, QComboBox, QPushButton
from PyQt5uic import loadUi
from PyQt5.QtGui import QCloseEvent

from lib.load_piximage import load_piximage_from_url
from lib.pytube.streams import Stream
from lib.filesize import naturalsize
from threads.object_handle import VideoDownloadHandleThread, SelectStreamHandleThread, DownloadSubtitleHandleThread
from threading import Thread

from os.path import join
from os import startfile


class PlaylistDownloadWindow(QMainWindow):
    def __init__(self, download_data: dict, customized: bool, parent):
        super(PlaylistDownloadWindow, self).__init__()
        loadUi("./gui/playlist download", self)
        self.download_data = download_data
        self.videos_widgets = download_data["videos_data"]
        self.customized = customized
        self.main_window = parent
        self.playlist_title = self.download_data["playlist"].title
        self.setWindowTitle(self.playlist_title)

        # declare the window manipulators
        self.select_stream_handle = None
        self.download_handle = None
        self.subtitle_handle = None
        self.tasks = {}
        self.current_task = 0
        self.current_video = {}
        self.pause = False
        self.downloaded_bytes = 0

        self.key_bindings()
        self.display_global_data()
        self.display_items()

    def key_bindings(self):
        self.pause_resume_btn.clicked.connect(self.pause_resume)
        self.cancel_btn.clicked.connect(self.close)

    def display_global_data(self):
        self.url.setText(self.download_data["url"])
        self.location.setText(self.download_data["location"])
        Thread(target=self.display_thumbnail, daemon=True).start()

    def display_thumbnail(self):
        playlist_thumbnail = self.download_data["playlist"].videos[0].thumbnail_url
        playlist_thumbnail = load_piximage_from_url(playlist_thumbnail)
        if playlist_thumbnail:
            self.playlist_img.setPixmap(playlist_thumbnail.scaledToWidth(243))
        else:
            self.playlist_img.setStyleSheet(self.playlist_img.styleSheet() + "color: #f32013;")
            self.playlist_img.setText("Failed!")

    def display_items(self):
        videos = self.download_data["videos_data"]
        counter = 0
        for video in videos:
            subtitle = "no subtitle"
            subtitle_index = 0
            if self.customized:
                # handles cutomized playlists
                customized_data = videos[video]["customized_data"]
                template = videos[video]["template"]
                subtitle_combobox = template.findChild(QComboBox, "subtitles")
                if customized_data["subtitle"] != subtitle:
                    subtitle = customized_data["subtitle"]
                    subtitle_index = customized_data["subtitle_index"]
                if customized_data["include"]:
                    stream_type = customized_data["stream_type"]
                    quality = ["quality"]
                else:
                    # neglects the unchecked videos
                    continue
            else:
                stream_type = self.download_data["stream_type"]
                quality = self.download_data["quality"]

            self.items_area.addWidget(self.videos_widgets[video]["item"])
            self.tasks[counter] = {
                "video": video,
                "item": videos[video]["item"],
                "video_data": videos[video]["video_data"],
                "type": stream_type,
                "quality": quality,
                "subtitle": subtitle,
                "subtitle_index": subtitle_index,
                "done": False
            }
            counter += 1

    def display_current_video_data(self):
        video_data = self.tasks[self.current_task]["video_data"]
        self.title.setText(video_data["title"])
        self.author.setText(video_data["author"])
        self.length.setText(video_data["length"])
        self.quality.setText("fetching ..")
        self.size.setText("fetching ..")
        if video_data["image"]:
            self.current_video_img.setPixmap(video_data["image"].scaledToWidth(243))
        else:
            self.current_video_img.setStyleSheet(self.current_video_img.styleSheet() + "color: #f32013;")
            self.current_video_img.setText("Failed!")
        self.statusBar().showMessage(f"preparing {video_data['title']} ..")

    def display_download_stat(self, stat: dict):
        template = self.tasks[self.current_task]["item"]
        template.status.setText(f"{str(naturalsize(stat['downloaded']))} / {naturalsize(stat['estimated_size'])}"
                                f"    {stat['estimated_time']}")
        template.progress.setValue(stat["progress"])
        template.progress_label.setText(f"Progress:  {stat['progress']}%")
        self.downloaded_bytes += stat["downloaded"]

        self.rate.setText(naturalsize(stat['rate']))
        self.downloaded.setText(str(naturalsize(self.downloaded_bytes)))
        self.estimated.setText(f"{len(self.tasks) - self.current_task - 1} items")
        playlist_progress = int(100 * (self.current_task + (stat["progress"] / 100)) / len(self.tasks))
        self.progress.setValue(playlist_progress)
        self.progress_label.setText(f"Progress:  {playlist_progress}%")

    def manage_tasks(self):
        current_task = self.tasks.get(self.current_task)
        if current_task:
            prefix = str(self.current_task + 1).zfill(len(str(len(self.tasks)))) if self.download_data[
                "numbered"] else None
            self.select_stream_handle = SelectStreamHandleThread(current_task=current_task,
                                                                 video_object=
                                                                 self.videos_widgets[current_task["video"]]["video"],
                                                                 location=self.download_data["location"],
                                                                 prefix=prefix)
            self.select_stream_handle.on_selected.connect(self.download_stream)
            self.select_stream_handle.on_error.connect(self.on_error)
            self.select_stream_handle.start()
            self.display_current_video_data()
        # trigger end of videos
        else:
            self.statusBar().showMessage("All tasks finished")
            self.on_tasks_finished(
                title=self.playlist_title,
                folder=self.download_data["location"])

    def next_task(self):
        self.tasks[self.current_task]["done"] = True
        self.current_task += 1
        self.manage_tasks()

    def download_stream(self, kwargs):
        # stop and wait for previous tasks' threads

        self.quality.setText(f"{kwargs['stream'].resolution} (progressive)")
        self.size.setText(str(naturalsize(kwargs['stream'].filesize)))

        if self.download_handle:
            self.download_handle.analyzer.quit()
            self.download_handle.analyzer.wait()
            self.download_handle.quit()
            self.download_handle.wait()

        self.download_handle = VideoDownloadHandleThread(
            stream=kwargs["stream"],
            file_path=kwargs["location"],
            filesize=kwargs["stream"].filesize
        )
        self.download_handle.download_stat.connect(self.display_download_stat)
        self.download_handle.analyzer.completed.connect(self.on_current_video_downloaded)
        self.download_handle.on_error.connect(self.on_error)
        self.download_handle.start()
        self.statusBar().showMessage(f"downloading {kwargs['title']} ..")

    def on_current_video_downloaded(self):
        current_task = self.tasks[self.current_task]
        if current_task["subtitle"] != "no subtitle":
            self.subtitle_handle = DownloadSubtitleHandleThread(subtitle=current_task["subtitle"],
                                                                title=current_task["video"],
                                                                location=self.download_data["location"],
                                                                index=current_task["subtitle_index"])
            self.subtitle_handle.finished.connect(lambda: current_task["item"].status.setText("finished"))
            self.subtitle_handle.finished.connect(self.next_task)
            self.subtitle_handle.start()
        else:
            current_task["item"].status.setText("finished")
            self.next_task()

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

    def on_tasks_finished(self, title: str = "", folder: str = ""):
        file_path = self.download_data['location']
        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Download Finished")
        msg.setIcon(QMessageBox.Information)
        msg.setText(title)
        open_folder = QPushButton("open folder")
        download_another = QPushButton("download another")
        exit_btn = QPushButton("exit")
        msg.addButton(open_folder, QMessageBox.AcceptRole)
        msg.addButton(download_another, QMessageBox.AcceptRole)
        msg.addButton(exit_btn, QMessageBox.AcceptRole)
        btn = msg.exec_()

        if btn == 0:
            startfile(folder)
        elif btn == 1:
            self.prepare_another()
            return
        exit()

    def on_error(self, e: str = None):
        msg = QMessageBox(parent=self)
        msg.setWindowTitle("Error!")
        msg.setIcon(QMessageBox.Critical)
        msg.setText(f"Error happened while downloading {e if e else ''}")
        msg.addButton("Try again", QMessageBox.AcceptRole)
        msg.addButton("Exit", QMessageBox.AcceptRole)
        btn = msg.exec()

        if btn == 0:
            self.manage_tasks()
        else:
            exit()

    def prepare_another(self):
        self.hide()
        self.main_window.reset_gui(playlist_tab=True)
        self.main_window.show()
