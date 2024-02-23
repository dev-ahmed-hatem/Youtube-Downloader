from PyQt5.QtGui import QImage, QPixmap
from requests import get


def load_piximage_from_url(url):
    try:
        image = QImage()
        image.loadFromData(get(url).content)
        return QPixmap(image)
    except Exception:
        return None
