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
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QLabel, QPushButton
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
from webbrowser import open as open_link
from json import load


def show_message_box(text, title, link=None, error=False):
    app = QApplication([])
    apply_stylesheet(app, "dark_teal.xml")

    msg_box = QMessageBox()
    msg_box.setText(text)
    msg_box.setWindowTitle(title)
    msg_box.setIcon(QMessageBox.Critical if error else QMessageBox.Information)
    download_btn = None
    if link:
        download_btn = msg_box.addButton("Download", QMessageBox.AcceptRole)
    exit_btn = msg_box.addButton("Exit", QMessageBox.RejectRole)
    msg_box.exec_()

    if msg_box.clickedButton() == download_btn:
        open_link(link)

    sys.exit()


def current_version():
    with open("./_internal/init.json", "r") as init:
        version = load(init)["version"]
        init.close()
        return version


def check_updates():
    try:
        server_data = requests.get("https://dev-ahmed-hatem.github.io/Youtube-Downloader/init.json").json()
        execute = server_data["execute"]
        latest_version = server_data["version"]
        link = server_data["link"] or False
        if not execute or latest_version != current_version():
            update_message = f"A newer version ({latest_version}) was found.\nPlease update the program"
            show_message_box(update_message, "Update Required", link=link)

    except Exception as e:
        print(e)
        show_message_box("Couldn't fetch server data\nPlease check your internet connection", "Connection Error",
                         error=True)


if __name__ == "__main__":
    check_updates()
    dirs.prepare_download_location()

    # define the app
    app = QApplication([])
    apply_stylesheet(app, "dark_teal.xml")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
