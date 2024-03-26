# import MainWindow and gui modules
from windows.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from qt_material import apply_stylesheet
from lib import dirs

# imports to be included in building
# import additional lib
from pytube import YouTube
from pytube.exceptions import RegexMatchError
from pytube.helpers import safe_filename
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

# import gui modules
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QLabel
from PyQt5uic import loadUi

# hidden imports
import os
import sys
import lib
import requests
import urllib3
from PyQt5 import Qt
import merging
import numpy
import pkg_resources
import youtube_transcript_api

if __name__ == "__main__":
    dirs.prepare_download_location()

    # define the app
    app = QApplication([])
    apply_stylesheet(app, "dark_teal.xml")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


def check_updates():
    server_data = requests.get("")
    version = 0
    update_message = f"A newer version ({version}) was found.\nPlease update the program"


    return
    msg = PyQt5.QtWidgets.QMessageBox()
    msg.setWindowTitle("")
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
