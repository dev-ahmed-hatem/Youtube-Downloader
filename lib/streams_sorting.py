def sort(arr):
    arr = list(arr)
    length = len(arr)
    for i in range(length):
        for j in range(0, length - i - 1):
            if arr[j].filesize > arr[j + 1].filesize:
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
    return arr


def pick_appropriate_audio_stream(resolution: str, audio_streams):
    match resolution:
        case "1080p":
            selected_audio_stream = audio_streams[-1]
        case "720p":
            if len(audio_streams) > 1:
                selected_audio_stream = audio_streams[-2]
            else:
                selected_audio_stream = audio_streams[-1]
        case "480p" | "360p":
            if len(audio_streams) > 2:
                selected_audio_stream = audio_streams[-3]
            else:
                selected_audio_stream = audio_streams[0]
        case "240p":
            if len(audio_streams) > 3:
                selected_audio_stream = audio_streams[-4]
            else:
                selected_audio_stream = audio_streams[0]
        case "144p":
            selected_audio_stream = audio_streams[0]
        case _:
            selected_audio_stream = audio_streams[0]
    return selected_audio_stream


def justify_streams(audio_streams, video_streams):
    streams = {}
    audio_streams = sort(list(audio_streams))
    video_streams = list(video_streams)
    for i in range(len(video_streams)):
        streams[f"{i}"] = {"video": video_streams[i],
                           "audio": pick_appropriate_audio_stream(video_streams[i].resolution, audio_streams)
                           }
    return streams
