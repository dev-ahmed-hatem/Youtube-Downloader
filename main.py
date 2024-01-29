# add additional libs to path
import sys

sys.path.append("./lib")
sys.path.append("./lib/pytube")
sys.path.append("./threads")
sys.path.append("./windows")

# import additional libs
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.helpers import safe_filename
from filesize import naturalsize
from streams_sorting import justify_streams
from thread_handler import initiate_thread

# import threading modules
from object_handle import VideoHandleThread, SubtitleHandleThread, PlaylistHandleThread, CustomizingHandleThread

# import different windows
from windows.customize_playlist import CustomizingWindow
from windows.video_template import VideoTemplate

# import necessary modules
from threading import Thread
from os import path, makedirs

# import gui modules
from PyQt5.Qt import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QLineEdit, QFileDialog, QLabel
from PyQt5.uic import loadUi
from lib.qt_material import apply_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # define threads handlers attributes
        self.video_handle_thread = None
        self.subtitle_handle_thread = None
        self.playlist_handle_thread = None
        self.customizing_handle_thread = None

        # define video / playlist attributes
        self.current_video = {}
        self.current_playlist = {}

        # windows attributes
        self.customize_window = None

        self.reset_gui()

    # specific for gui actions
    def reset_gui(self, playlist_tab=False):
        loadUi("./gui/main window", self)

        # resetting threads
        if self.video_handle_thread:
            self.video_handle_thread.terminate()
        if self.playlist_handle_thread:
            self.playlist_handle_thread.terminate()
        if self.subtitle_handle_thread:
            self.subtitle_handle_thread.terminate()

        # resetting video tab
        self.video_save_location.setEnabled(False)
        self.video_browse_b.setEnabled(False)
        self.video_type_group.setEnabled(False)
        self.video_quality.setEnabled(False)
        self.video_subtitle.setEnabled(False)
        self.video_download_b.setEnabled(False)

        # resetting playlist tab
        self.playlist_save_location.setEnabled(False)
        self.playlist_browse_b.setEnabled(False)
        self.playlist_type_group.setEnabled(False)
        self.playlist_quality.setEnabled(False)
        self.playlist_customize_b.setEnabled(False)
        self.playlist_download_b.setEnabled(False)
        if playlist_tab:
            self.tabs.setCurrentIndex(1)

        self.key_bindings()

    def disable_gui(self):
        self.video_get_b.setEnabled(False)
        # self.video_reset_b.setEnabled(False)
        self.video_url.setEnabled(False)
        self.playlist_get_b.setEnabled(False)
        self.playlist_reset_b.setEnabled(False)
        self.playlist_url.setEnabled(False)

    def key_bindings(self):
        # define key bindings for video tab
        self.video_get_b.clicked.connect(self.get_video)
        self.video_browse_b.clicked.connect(self.get_video_save_location)
        self.video_radio.clicked.connect(lambda: self.show_streams("video"))
        self.audio_radio.clicked.connect(lambda: self.show_streams("audio"))
        self.video_reset_b.clicked.connect(self.reset_gui)
        self.video_download_b.clicked.connect(self.fetch_video_download_data)

        # define key bindings for playlist tab
        self.playlist_get_b.clicked.connect(self.get_playlist)
        self.playlist_browse_b.clicked.connect(self.get_playlist_save_location)
        self.playlist_videos_radio.clicked.connect(lambda: self.change_playlist_type("videos"))
        self.playlist_audios_radio.clicked.connect(lambda: self.change_playlist_type("audios"))
        self.playlist_quality.currentIndexChanged.connect(self.change_playlist_quality)
        self.playlist_reset_b.clicked.connect(lambda: self.reset_gui(True))
        self.playlist_customize_b.clicked.connect(self.customize_playlist)

    # specific for video handling
    def get_video(self):
        url = self.video_url.text()
        self.disable_gui()
        try:
            # initiate YouTube object
            video = YouTube(url)

            # initiate video handle thread
            self.video_handle_thread = VideoHandleThread(video=video, parent=self)
            self.video_handle_thread.error.connect(self.receive_message_from_thread)
            self.video_handle_thread.display_video_data.connect(self.display_video_data)
            self.video_handle_thread.start()
            self.statusBar().showMessage("Getting video data .. please wait.")

            # initiate subtitle handle thread
            self.subtitle_handle_thread = SubtitleHandleThread(video.video_id, self)
            self.subtitle_handle_thread.display_subtitles.connect(self.display_subtitles)
            self.subtitle_handle_thread.start()

        except RegexMatchError:
            self.show_message(QMessageBox.Critical, "Invalid URL!")
        except Exception:
            self.show_message(QMessageBox.Critical, "Unexpected Error!")

    def display_video_data(self):
        self.statusBar().showMessage("Ready to download")
        self.define_video_filename()
        self.show_streams("video")
        self.video_browse_b.setEnabled(True)
        self.video_type_group.setEnabled(True)
        self.video_radio.setChecked(True)
        self.video_quality.setEnabled(True)
        self.video_subtitle.setEnabled(True)
        self.video_reset_b.setEnabled(True)
        self.video_download_b.setEnabled(True)

    def define_video_filename(self):
        video_filename = self.current_video["streams"].filter(only_video=True)[0].default_filename
        audio_filename = self.current_video["streams"].filter(only_audio=True)[0].default_filename
        self.current_video["video_filename"] = path.join(videos_dir, video_filename)
        self.current_video["audio_filename"] = path.join(audios_dir, audio_filename)

    def get_video_save_location(self):
        file_location, _ = QFileDialog.getSaveFileName(parent=self,
                                                       caption="Choose Location",
                                                       directory=self.current_video["video_filename"]
                                                       if self.video_radio.isChecked()
                                                       else self.current_video["audio_filename"]
                                                       )
        self.video_save_location.setText(file_location)

    def show_streams(self, streams_type: str):
        counter = 0
        items = {}
        if streams_type == "video":
            self.video_save_location.setText(self.current_video["video_filename"])
            for stream in self.current_video["streams"].filter(progressive=True):
                items[counter] = {
                    "type": "progressive",
                    "display": f"{stream.mime_type} (merged)  {stream.resolution}  {naturalsize(stream.filesize)}",
                    "video": stream
                }
                counter += 1
            if ffmpeg_script():
                video_streams = self.current_video["streams"].filter(only_video=True)
                audio_streams = self.current_video["streams"].filter(only_audio=True)
                unmerged = justify_streams(audio_streams, video_streams)
                for stream in unmerged:
                    vid = unmerged[stream]["video"]
                    aud = unmerged[stream]["audio"]
                    items[counter] = {
                        "type": "unmerged",
                        "display":
                            f"{vid.mime_type} (unmerged)  {vid.resolution}  {naturalsize(vid.filesize + aud.filesize)}",
                        "video": vid,
                        "audio": aud,
                    }

                    counter += 1
        else:
            self.video_save_location.setText(self.current_video["audio_filename"])
            for stream in self.current_video["streams"].filter(only_audio=True):
                items[counter] = {
                    "type": "audio",
                    "display": f"{stream.mime_type} (audio)  {naturalsize(stream.filesize)}",
                    "audio": stream
                }
                counter += 1

        self.video_quality.clear()
        self.current_video["resolved_streams"] = items
        for item in items:
            self.video_quality.addItem(items[item]["display"])

    def display_subtitles(self):
        self.video_subtitle.addItem("no subtitle")

        if self.current_video["subtitles_display"]:
            for subtitle in self.current_video["subtitles_display"]:
                self.video_subtitle.addItem(subtitle)

    def fetch_video_download_data(self):
        save_location = self.video_save_location.text()
        if save_location == "":
            self.show_message(QMessageBox.Warning, "Choose save location", False)
            return
        quality = self.video_quality.currentIndex()
        subtitle = self.video_subtitle.currentIndex()
        print(f"save_location: {save_location}")
        print(f"stream: {self.current_video['resolved_streams'][quality]}")
        print(f"subtitle: {self.current_video['subtitle_object'].get_lang_code(subtitle - 1)}"
              if subtitle != 0
              else "no subtitle")

    # specific for playlist handling
    def get_playlist(self):
        url = self.playlist_url.text()
        self.disable_gui()

        # initiate playlist handle thread
        self.playlist_handle_thread = PlaylistHandleThread(url, self)
        self.playlist_handle_thread.handle_size = False
        self.playlist_handle_thread.error.connect(self.receive_message_from_thread)
        self.playlist_handle_thread.display_playlist_data.connect(self.display_playlist_data)
        self.playlist_handle_thread.display_playlist_size.connect(self.change_playlist_quality)
        self.playlist_handle_thread.start()
        self.statusBar().showMessage("Getting playlist data .. please wait.")

    def get_playlist_size(self):
        self.playlist_handle_thread.handle_size = True
        self.playlist_handle_thread.start()

    def display_playlist_data(self):
        self.current_playlist["ui_changed"] = False
        self.current_playlist["customized"] = False
        self.current_playlist["download_data"] = {}
        self.approx_size_title.setText("Approx Size: ")
        self.approx_size.setText("calculating ..")
        self.get_playlist_size()
        self.collect_playlist_videos_data()
        self.statusBar().showMessage(self.current_playlist["playlist_title"])
        self.playlist_count.setText(str(self.current_playlist["playlist_count"]))
        self.define_playlist_filename()
        self.playlist_save_location.setText(self.current_playlist["playlist_location"])
        self.playlist_browse_b.setEnabled(True)
        self.playlist_type_group.setEnabled(True)
        self.playlist_videos_radio.setChecked(True)
        self.playlist_quality.setEnabled(True)
        self.playlist_reset_b.setEnabled(True)
        self.playlist_download_b.setEnabled(True)

        self.playlist_quality.addItem("Normal")
        self.playlist_quality.addItem("Low")

    def display_playlist_size(self, mul_factor: int):
        if not self.current_playlist.get("size"):
            return
        size = 0
        for duration in self.current_playlist["playlist_videos_durations"]:
            size += duration * mul_factor
        self.approx_size.setText(naturalsize(size))

    def define_playlist_filename(self):
        playlist_dirname = safe_filename(self.current_playlist["playlist_title"])
        self.current_playlist["playlist_location"] = path.join(playlists_dir, playlist_dirname)

    def get_playlist_save_location(self):
        playlist_location = QFileDialog.getExistingDirectory(parent=self,
                                                             caption="Choose Location",
                                                             directory=self.current_playlist["playlist_location"])
        self.playlist_save_location.setText(playlist_location)

    def change_playlist_type(self, streams_type: str):
        if not self.current_playlist.get("size"):
            return
        self.playlist_quality.setCurrentIndex(0)
        self.display_playlist_size(self.current_playlist["playlist_mul_factor"]
                                   [f"normal {'progressive' if streams_type == 'videos' else 'audio'}"])

    def change_playlist_quality(self):
        try:
            if not self.current_playlist.get("size"):
                return
            qualities = {0: "normal", 1: "low"}
            compoBox = self.playlist_quality
            mul_factor = f"{qualities[compoBox.currentIndex()]}" \
                         f" {'progressive' if self.playlist_videos_radio.isChecked() else 'audio'}"
            self.display_playlist_size(self.current_playlist["playlist_mul_factor"][mul_factor])
        except Exception:
            pass

    def collect_playlist_videos_data(self):
        self.customizing_handle_thread = CustomizingHandleThread(self.current_playlist["playlist"], self)
        self.customizing_handle_thread.finished.connect(self.prepare_video_templates)
        self.customizing_handle_thread.finished.connect(lambda: self.playlist_customize_b.setEnabled(True))
        self.customizing_handle_thread.start()

    def prepare_video_templates(self):
        for video in self.current_playlist["download_data"]:
            self.current_playlist["download_data"][video]["template"] = VideoTemplate(
                self.current_playlist["download_data"][video]["video_data"]
            )
        self.customize_window = CustomizingWindow(
            self.current_playlist["playlist_title"],
            self.current_playlist["download_data"],
        )
        self.customize_window.playlist_custom_data.connect(self.receive_custom_download_data)

    def customize_playlist(self):
        if self.current_playlist["customized"]:
            for video in self.current_playlist["download_data"]:
                self.customize_window.load_saved_changes(
                    template=self.current_playlist["download_data"][video]["template"],
                    customized_data=self.current_playlist["download_data"][video]["customized_data"]
                )
        else:
            self.customize_window.set_defaults()
        self.customize_window.check_selection()
        self.customize_window.exec()

        if self.current_playlist["customized"] and not self.current_playlist["ui_changed"]:
            self.playlist_type_group.deleteLater()
            self.playlist_quality.deleteLater()
            self.approx_size.deleteLater()
            self.approx_size_title.deleteLater()
            label1 = QLabel("Open customizing window", self)
            label2 = QLabel("Open customizing window", self)
            self.grid_layout.addWidget(label1, 2, 1, 1, 2)
            self.grid_layout.addWidget(label2, 3, 1, 1, 2)
            self.current_playlist["ui_changed"] = True

    def receive_custom_download_data(self, data):
        self.current_playlist["download_data"] = data
        self.current_playlist["customized"] = True

    # specific for user messaging
    def receive_message_from_thread(self, msg_type, txt, reset_gui=True, playlist_tab=False):
        if msg_type == "critical":
            msg_type = QMessageBox.Critical
        elif msg_type == "information":
            msg_type = QMessageBox.Information
        else:
            msg_type = QMessageBox.Warning
        self.show_message(msg_type, txt, reset_gui, playlist_tab)

    def show_message(self, msg_type, txt, reset_gui=True, playlist_tab=False):
        msg = QMessageBox(parent=self)
        if msg_type == QMessageBox.Critical:
            msg.setWindowTitle("Error")
        elif msg_type == QMessageBox.Information:
            msg.setWindowTitle("Information")
        else:
            msg.setWindowTitle("Warning")
        msg.setIcon(msg_type)
        msg.setText(txt)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()
        if reset_gui:
            self.reset_gui(playlist_tab)


# define download locations if not exists
videos_dir, audios_dir, playlists_dir = "", "", ""


# check whether ffmpeg script is found
def ffmpeg_script() -> bool:
    return path.exists("./lib/ffmpeg.exe")


def prepare_download_location():
    global videos_dir, audios_dir, playlists_dir
    downloads_folder = path.join(path.expanduser("~"), "Downloads")
    base_dir = path.join(downloads_folder, "YouTube Downloads")
    videos_dir = path.join(base_dir, "Videos")
    audios_dir = path.join(base_dir, "Audios")
    playlists_dir = path.join(base_dir, "Playlists")
    download_dirs = [base_dir, videos_dir, audios_dir, playlists_dir]
    for directory in download_dirs:
        if not path.exists(directory):
            makedirs(directory)


# https://www.youtube.com/watch?v=RBSGKlAvoiM&pp=ygUicHl0aG9uIGRhdGEgc3RydWN0dXJlcyBmdWxsIGNvdXJzZQ%3D%3D

# https://www.youtube.com/playlist?list=PLMSBalys69yzbmRgoceGUidP8B7fir1dx

if __name__ == "__main__":
    prepare_download_location()

    # define the app
    app = QApplication([])
    apply_stylesheet(app, "dark_teal.xml")
    window = MainWindow()
    window.show()
    app.exec()
