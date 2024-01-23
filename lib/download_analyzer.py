from os.path import getsize
from filesize import naturalsize
from time import sleep


class DownloadAnalyzer:
    def __init__(self, filename: str, length: int, callback):
        self.filename = filename
        self.length = length
        self.lastSize = 0
        self.callback = callback
        self.flag = True

    def analyze(self, delay):
        while self.flag:
            currentSize = getsize(self.filename)
            rate = (currentSize - self.lastSize) / delay
            estimatedSize = self.length - currentSize
            estimatedTime = DownloadAnalyzer.standard_time(estimatedSize / rate) if rate else "N/A"
            self.lastSize = currentSize
            data = {
                "rate": rate,
                "downloaded": currentSize,
                "estimated-size": estimatedSize,
                "estimated-time": estimatedTime,
                "progress": int((currentSize/self.length) * 100)
            }
            self.callback(data)
            sleep(delay)

    @staticmethod
    def standard_time(seconds):
        currentSeconds = int(seconds % 60)
        minutes = int(seconds // 60)
        currentMinutes = int(minutes % 60)
        hours = int(minutes // 60)
        return f"{str(hours).zfill(2)}:{str(currentMinutes).zfill(2)}:{str(currentSeconds).zfill(2)}"
