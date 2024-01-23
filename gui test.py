from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QVBoxLayout, QScrollArea
from PyQt5.uic import loadUi


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        loadUi("gui/playlist customizing window.ui", self)

        frame = self.frame
        print(frame)

        from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout
        import sys


class MainWindow2(QWidget):
    def __init__(self):
        super().__init__()

        # Load the UI file created by Qt Designer
        # self.ui_template = loadUi("your_ui_file.ui")

        # Create a scroll area
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)

        # Create a widget to contain the template widgets
        content_widget = QWidget(scroll_area)
        scroll_area.setWidget(content_widget)

        # Create a layout for the content widget
        content_layout = QVBoxLayout(content_widget)

        # Add multiple instances of the template widget to the content layout
        for _ in range(1000):
            template_instance = self.createTemplateInstance()
            content_layout.addWidget(template_instance)

        # Set up the main layout
        main_layout = QVBoxLayout(self)
        main_layout.addWidget(scroll_area)

    def createTemplateInstance(self):
        # Create a new instance of the template widget
        new_instance = QWidget()
        loadUi("gui/template.ui", new_instance)  # Load the UI into the new instance
        return new_instance


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow2()
    window.show()
    app.exec()
