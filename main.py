# import MainWindow and gui modules
from windows.main_window import MainWindow
from PyQt5.QtWidgets import QApplication
from lib.qt_material import apply_stylesheet
from lib import dirs


# https://www.youtube.com/watch?v=RBSGKlAvoiM&pp=ygUicHl0aG9uIGRhdGEgc3RydWN0dXJlcyBmdWxsIGNvdXJzZQ%3D%3D

# https://www.youtube.com/playlist?list=PLMSBalys69yzbmRgoceGUidP8B7fir1dx


# https://www.youtube.com/watch?v=gb7pZZKqFoE

if __name__ == "__main__":
    dirs.prepare_download_location()

    # define the app
    app = QApplication([])
    apply_stylesheet(app, "dark_teal.xml")
    window = MainWindow()
    window.show()
    app.exec()


def print_dict(data: dict):
    print(data)


def merge():
    from lib.merging.moviepy.editor import VideoFileClip, AudioFileClip
    audio = AudioFileClip("./playground/b.webm")
    video = VideoFileClip("./playground/a.mp4")

    video = video.set_audio(audio)
    video.write_videofile("./playground/result2.mp4", codec='libx264', audio_codec='aac', verbose=False,
                          monitor_callback=print_dict)
    # video.write_video
