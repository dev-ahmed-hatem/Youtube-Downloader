from os.path import getsize
from filesize import naturalsize
from time import sleep
from threading import Thread
from time_format import standard_time


class DownloadAnalyzer:
    def __init__(self, file: str, length: int, callback=None):
        self.filename = file
        self.length = length
        self.lastSize = 0
        self.callback = callback
        self.flag = True

    def analyze(self, delay):
        while self.flag:
            currentSize = getsize(self.filename)
            rate = (currentSize - self.lastSize) / delay
            estimatedSize = self.length - currentSize
            estimatedTime = standard_time(estimatedSize / rate) if rate else "N/A"
            self.lastSize = currentSize
            data = {
                "rate": rate,
                "downloaded": currentSize,
                "estimated_size": estimatedSize,
                "estimated_time": estimatedTime,
                "progress": int((currentSize / self.length) * 100)
            }
            print(data)
            if self.callback:
                self.callback(data)
            sleep(delay)

    def stop(self):
        self.flag = False

"""
import requests


def download_file(url, destination):
    # Send a GET request to the URL
    response = requests.get(url)
    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Open the destination file in binary write mode and write the contents of the response
        with open(destination, 'wb') as f:
            Thread(target=DownloadAnalyzer("Fall.mp4", getsize("falle.mp4")).analyze, kwargs={"delay": 0.8},
                   daemon=True).start()
            # Iterate over the response content in chunks
            for chunk in response.iter_content(chunk_size=10):
                # Write the chunk to the file
                f.write(chunk)
        print("File downloaded successfully.")
    else:
        print("Failed to download file. Status code:", response.status_code)


# Example usage:
url = "http://127.0.0.1:5500/Fall.mp4"
destination = "Fall.mp4"
download_file(url, destination)
"""