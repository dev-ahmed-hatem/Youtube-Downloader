import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Main Window')

        self.label = QLabel('Main Window')
        self.button = QPushButton('Show Secondary Window')
        self.button.clicked.connect(self.showSecondaryWindow)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.button)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def showSecondaryWindow(self):
        self.hide()  # Hide the main window
        self.secondary_window = SecondaryWindow()
        self.secondary_window.show()

class SecondaryWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Secondary Window')

        self.label = QLabel('Secondary Window')

        layout = QVBoxLayout()
        layout.addWidget(self.label)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        # When the secondary window is closed, show the main window again
        event.accept()
        main_window.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
