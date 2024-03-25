# import additional lib
from lib.pytube import YouTube
from lib.pytube.exceptions import RegexMatchError
from lib.pytube.helpers import safe_filename
from lib.filesize import naturalsize
from lib.streams_sorting import justify_streams
from lib.time_format import standard_time

# import threading modules
from threads.object_handle import VideoHandleThread, SubtitleHandleThread, PlaylistHandleThread, \
    CustomizingHandleThread, PlaylistThumbnailsHandle

# import different windows
from windows.customize_playlist import CustomizingWindow, load_customized_data
from windows.video_download import VideoDownloadWindow
from windows.video_template import VideoTemplate
from windows.playlist_download import PlaylistDownloadWindow
from windows.playlist_item_template import PlaylistItemTemplate

# import necessary modules
from os import path
from lib import dirs

# import gui modules
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QLabel
from PyQt5uic import loadUi


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # define threads handlers attributes
        # TODO: collect them in a dictionary attribute
        self.video_handle_thread = None
        self.subtitle_handle_thread = None
        self.playlist_handle_thread = None
        self.customizing_handle_thread = None
        self.playlist_thumbnails_handle_thread = None

        # define video / playlist attributes
        self.current_video = {}
        self.current_playlist = {}

        # windows attributes
        self.customize_window = None
        self.video_download_window = None
        self.playlist_download_window = None

        self.reset_gui()

    # specific for gui actions
    def reset_gui(self, playlist_tab=False):
        loadUi("./gui/main window", self)

        self.current_video = {}
        self.current_playlist = {}

        # resetting threads
        if self.video_handle_thread:
            self.video_handle_thread.terminate()
        if self.playlist_handle_thread:
            self.playlist_handle_thread.terminate()
        if self.subtitle_handle_thread:
            self.subtitle_handle_thread.terminate()
        if self.customizing_handle_thread:
            self.customizing_handle_thread.terminate()
        if self.playlist_thumbnails_handle_thread:
            self.playlist_thumbnails_handle_thread.terminate()

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
        self.video_quality.currentIndexChanged.connect(self.define_stream_filename)
        self.playlist_quality.currentIndexChanged.connect(self.change_playlist_quality)
        self.playlist_reset_b.clicked.connect(lambda: self.reset_gui(True))
        self.playlist_customize_b.clicked.connect(self.customize_playlist)
        self.playlist_download_b.clicked.connect(self.fetch_playlist_download_data)

    # specific for video handling
    def get_video(self):
        url = self.video_url.text()
        self.disable_gui()
        try:
            # initiate YouTube object
            video = YouTube(url)
            self.current_video["video"] = video

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
        self.video_radio.setChecked(True)
        self.show_streams("video")
        self.video_browse_b.setEnabled(True)
        self.video_type_group.setEnabled(True)
        self.video_quality.setEnabled(True)
        self.video_subtitle.setEnabled(True)
        self.video_reset_b.setEnabled(True)
        self.video_download_b.setEnabled(True)

    def define_stream_filename(self):
        current = self.video_quality.currentIndex()
        if current == -1:
            return
        stream_type = "video" if self.video_radio.isChecked() else "audio"
        stream_filename = self.current_video["resolved_streams"][current][
            f"{stream_type}_stream_object"].default_filename
        if stream_type == "video":
            self.current_video["stream_file_location"] = path.join(dirs.videos_dir, stream_filename)
            self.video_save_location.setText(self.current_video["stream_file_location"])
        else:
            self.current_video["stream_file_location"] = path.join(dirs.audios_dir, stream_filename)
            self.video_save_location.setText(self.current_video["stream_file_location"])

    def get_video_save_location(self):
        current_location = self.video_save_location.text()
        file_location, _ = QFileDialog.getSaveFileName(parent=self,
                                                       caption="Choose Location",
                                                       directory=current_location if current_location else
                                                       self.current_video["stream_file_location"]
                                                       )
        self.video_save_location.setText(file_location)

    def show_streams(self, streams_type: str):
        counter = 0
        items = {}
        if streams_type == "video":
            for stream in self.current_video["streams"].filter(progressive=True):
                items[counter] = {
                    "type": "video",
                    "display": f"{stream.mime_type} (merged)  {stream.resolution}  {naturalsize(stream.filesize)}",
                    "video_stream_object": stream
                }
                counter += 1
            if dirs.ffmpeg_script():
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
                        "video_stream_object": vid,
                        "audio_stream_object": aud,
                    }

                    counter += 1
        else:
            for stream in self.current_video["streams"].filter(only_audio=True):
                items[counter] = {
                    "type": "audio",
                    "display": f"{stream.mime_type} (audio)  {naturalsize(stream.filesize)}",
                    "audio_stream_object": stream
                }
                counter += 1

        self.video_quality.currentIndexChanged.disconnect(self.define_stream_filename)
        self.video_quality.clear()
        self.current_video["resolved_streams"] = items
        for item in items:
            self.video_quality.addItem(items[item]["display"])
        self.video_quality.currentIndexChanged.connect(self.define_stream_filename)
        self.define_stream_filename()

    def display_subtitles(self):
        self.video_subtitle.addItem("no subtitle")

        if self.current_video["subtitles_display"]:
            for subtitle in self.current_video["subtitles_display"]:
                self.video_subtitle.addItem(subtitle)

    def fetch_video_download_data(self):
        # collect the data selected for the video
        save_location = self.video_save_location.text()
        if save_location == "":
            self.show_message(QMessageBox.Warning, "Choose save location", False)
            return
        download_data = {}
        current_video = self.current_video
        download_data["url"] = self.video_url.text()
        download_data["location"] = save_location
        quality_index = self.video_quality.currentIndex()
        subtitle_index = self.video_subtitle.currentIndex()
        download_data["title"] = current_video["video"].title
        download_data["author"] = current_video["video"].author
        download_data["length"] = standard_time(current_video["video"].length)
        current_video_selected_stream = current_video["resolved_streams"][quality_index]
        stream_type = current_video_selected_stream["type"]
        if stream_type == "video":
            video_stream_object = current_video_selected_stream["video_stream_object"]
            audio_stream_object = None
            download_data["quality"] = f"{video_stream_object.resolution} (progressive)"
            download_data["size"] = naturalsize(video_stream_object.filesize)
        elif stream_type == "unmerged":
            video_stream_object = current_video_selected_stream["video_stream_object"]
            audio_stream_object = current_video_selected_stream["audio_stream_object"]
            download_data["quality"] = f"video: {video_stream_object.resolution}   " \
                                       f"   audio: {audio_stream_object.abr}    (unmerged)"
            download_data["size"] = f"video: {naturalsize(video_stream_object.filesize)}   " \
                                    f"+   audio: {naturalsize(audio_stream_object.filesize)}"
        else:
            video_stream_object = None
            audio_stream_object = current_video_selected_stream["audio_stream_object"]
            download_data["quality"] = f"{audio_stream_object.abr} (audio)"
            download_data["size"] = naturalsize(audio_stream_object.filesize)
        download_data["thumbnail"] = current_video["video"].thumbnail_url
        download_data["subtitle_index"] = subtitle_index - 1 \
            if subtitle_index != 0 \
            else "no subtitle"
        download_data["subtitle_object"] = self.current_video["subtitle_object"]

        download_data["stream_type"] = stream_type
        download_data["video_stream_object"] = video_stream_object
        download_data["audio_stream_object"] = audio_stream_object

        # instantiate downloading window
        self.video_download_window = VideoDownloadWindow(download_data, self)
        self.hide()
        self.video_download_window.show()
        self.video_download_window.define_tasks()

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
        self.statusBar().showMessage("preparing videos to download ..")
        self.playlist_count.setText(str(self.current_playlist["playlist_count"]))
        self.define_playlist_filename()
        self.playlist_save_location.setText(self.current_playlist["playlist_location"])
        self.playlist_browse_b.setEnabled(True)
        self.playlist_type_group.setEnabled(True)
        self.playlist_videos_radio.setChecked(True)
        self.playlist_quality.setEnabled(True)
        self.playlist_reset_b.setEnabled(True)
        self.numbered.setEnabled(True)

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
        self.current_playlist["playlist_location"] = path.join(dirs.playlists_dir, playlist_dirname)

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
            combo_box = self.playlist_quality
            mul_factor = f"{qualities[combo_box.currentIndex()]}" \
                         f" {'progressive' if self.playlist_videos_radio.isChecked() else 'audio'}"
            self.display_playlist_size(self.current_playlist["playlist_mul_factor"][mul_factor])
        except Exception as e:
            print(e)

    def collect_playlist_videos_data(self):
        self.customizing_handle_thread = CustomizingHandleThread(self.current_playlist["playlist"], self)
        self.customizing_handle_thread.success.connect(self.prepare_video_templates)
        self.customizing_handle_thread.success.connect(self.collect_playlist_videos_thumbnails)
        self.customizing_handle_thread.success.connect(self.playlist_ready)
        self.customizing_handle_thread.start()

    def playlist_ready(self):
        self.playlist_customize_b.setEnabled(True)
        self.playlist_download_b.setEnabled(True)
        self.statusBar().showMessage(f"{self.current_playlist['playlist_title']} is ready to download")

    def collect_playlist_videos_thumbnails(self):
        self.playlist_thumbnails_handle_thread = PlaylistThumbnailsHandle(self.current_playlist["download_data"])
        self.playlist_thumbnails_handle_thread.start()

    def prepare_video_templates(self):
        download_data = self.current_playlist["download_data"]
        try:
            for index, video in enumerate(download_data, 1):
                download_data[video]["template"] = VideoTemplate(
                    download_data[video]["video_data"]
                )
                download_data[video]["item"] = PlaylistItemTemplate(
                video_data=download_data[video]["video_data"],
                order=index
            )
            self.customize_window = CustomizingWindow(
                self.current_playlist["playlist_title"],
                download_data,
            )
            self.customize_window.playlist_custom_data.connect(self.receive_custom_download_data)
        except KeyError:
            return

    def customize_playlist(self):
        if self.current_playlist["customized"]:
            for video in self.current_playlist["download_data"]:
                load_customized_data(template=self.current_playlist["download_data"][video]["template"],
                                     customized_data=self.current_playlist["download_data"][video]["customized_data"])
        else:
            self.customize_window.set_defaults()
        self.customize_window.check_selection()
        self.customize_window.exec()

        # notify the user in main window that the playlist is customized
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

    def fetch_playlist_download_data(self):
        # collect the data selected for the playlist
        save_location = self.playlist_save_location.text()
        if save_location == "":
            self.show_message(QMessageBox.Warning, "Choose save location", False)
            return
        customized = self.current_playlist["customized"]
        download_data = {
            "url": self.playlist_url.text(),
            "location": save_location,
            "numbered": self.numbered.isChecked(),
            "playlist": self.current_playlist["playlist"],
            "videos_data": self.current_playlist["download_data"]
        }
        if not customized:
            download_data["stream_type"] = "video" if self.playlist_videos_radio.isChecked() else "audio"
            download_data["quality"] = "normal" if self.playlist_quality.currentIndex() == 0 else "low"

        self.playlist_download_window = PlaylistDownloadWindow(download_data=download_data,
                                                               customized=customized,
                                                               parent=self)
        self.playlist_download_window.show()
        self.playlist_download_window.manage_tasks()
        self.hide()

    def prepare_playlist_download_window(self):
        self.playlist_download_window = None

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
