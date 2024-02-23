def standard_time(seconds):
    currentSeconds = int(seconds % 60)
    minutes = int(seconds // 60)
    currentMinutes = int(minutes % 60)
    hours = int(minutes // 60)
    return f"{str(hours).zfill(2)}:{str(currentMinutes).zfill(2)}:{str(currentSeconds).zfill(2)}"
