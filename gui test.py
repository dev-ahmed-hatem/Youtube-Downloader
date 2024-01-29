from PyQt5.QtCore import QThread, pyqtSignal, QObject
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QPushButton, QWidget
import sys

class WorkerThread(QThread):
    finished = pyqtSignal()

    def run(self):
        # try:
            # Simulate work or call a function that fetches data
        self.fetch_data()
        """except Exception as e:
            print(f"Exception in worker thread: {e}")
        finally:
            self.finished.emit()"""

    def fetch_data(self):
        # Simulate fetching data or perform actual work
        for i in range(5):
            print(f"Fetching data... {i}")
            self.sleep(1)  # Simulate work (do not use time.sleep in a QThread)

class WorkerController(QObject):
    def __init__(self):
        super().__init__()

        self.thread = WorkerThread()
        self.thread.finished.connect(self.handle_thread_finished)

    def start_thread(self):
        self.thread.start()

    def stop_thread(self):
        # Forcefully terminate the thread
        self.thread.terminate()

    def handle_thread_finished(self):
        print("Thread finished.")

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Thread Termination Example")
        self.setGeometry(100, 100, 400, 200)

        layout = QVBoxLayout()

        start_button = QPushButton("Start Thread", self)
        start_button.clicked.connect(self.start_thread)

        stop_button = QPushButton("Stop Thread", self)
        stop_button.clicked.connect(self.stop_thread)

        layout.addWidget(start_button)
        layout.addWidget(stop_button)

        self.setLayout(layout)

        self.worker_controller = WorkerController()

    def start_thread(self):
        self.worker_controller.start_thread()

    def stop_thread(self):
        self.worker_controller.stop_thread()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())