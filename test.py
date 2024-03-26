# add additional lib to path
import sys

sys.path.append("lib")
sys.path.append("lib/pytube")
from pytube import Playlist, YouTube, Stream
from lib.filesize import naturalsize

video = YouTube("https://www.youtube.com/watch?v=HFWQdGn5DaU")

streams = video.streams.filter(only_video=True, subtype="mp4")
print(streams)
# subtitle_object = Subtitle(video_id=id)
# print(subtitle_object.get_subtitles())
# print(subtitle_object.generate_srt_format(27))


# print(videoStreams[1].get_file_path())


exit()
# https://www.youtube.com/playlist?list=PLH2l6uzC4UEW0s7-KewFLBC1D0l6XRfye 2.2 GB
# https://www.youtube.com/playlist?list=PLMSBalys69yzbmRgoceGUidP8B7fir1dx 1.3 GB
# https://www.youtube.com/playlist?list=PLkH1REggdbJpFXAzQqpjZgV1oghPsf9OH 880.5 MB
# https://www.youtube.com/watch?v=fzJKhWpJRXM&list=PL-hlJtdAqBx0v9O7s9vYJnLbCOT9GN-wW 1.7 GB


# https://www.youtube.com/watch?v=kiUGf_Z08RQ&list=PL43pGnjiVwgTg9IGE0ijSMDxVG66Lhye2&index=2&pp=iAQB
# https://www.youtube.com/watch?v=GQp1zzTwrIg&list=PL43pGnjiVwgTg9IGE0ijSMDxVG66Lhye2&index=1

play = Playlist("https://www.youtube.com/watch?v=fzJKhWpJRXM&list=PL-hlJtdAqBx0v9O7s9vYJnLbCOT9GN-wW")


def playlist_approx_size(playlist: Playlist):
    first_video = playlist.videos[0]
    mul_factor = first_video.streams.filter(progressive=True)[-1].filesize / first_video.length
    print(mul_factor)

    videos = list(playlist.videos)
    size = 0
    for video in videos:
        video_size = video.length * mul_factor
        size += video_size
        print(naturalsize(video_size))
    print(naturalsize(size))


def videoStreams(playlist: Playlist):
    first_video = playlist.videos[0].streams.filter(progressive=True)
    for stream in first_video:
        print(naturalsize(stream.filesize))


videoStreams(play)

"""
212.6 MB
259.8 MB
294.5 MB
600.4 MB
236.2 MB
142.8 MB
"""
