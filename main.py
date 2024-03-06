# import necessary modules
from os import path, makedirs

# import MainWindow and gui modules
from windows.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from lib.qt_material import apply_stylesheet


# define download locations if not exists
videos_dir, audios_dir, playlists_dir = "", "", ""


# check whether ffmpeg script is found
def ffmpeg_script() -> bool:
    # return path.exists("./lib/ffmpeg.exe")
    return True


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


# https://www.youtube.com/watch?v=gb7pZZKqFoE

if __name__ == "__main__":
    prepare_download_location()

    # define the app
    app = QApplication([])
    apply_stylesheet(app, "dark_teal.xml")
    window = MainWindow()
    window.show()
    app.exec()
