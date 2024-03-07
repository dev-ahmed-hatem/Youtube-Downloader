from os import path, makedirs

# define download locations if not exists
videos_dir, audios_dir, playlists_dir = "", "", ""


# check whether ffmpeg script is found
def ffmpeg_script() -> bool:
    # return path.exists("./lib/ffmpeg.exe")
    return True


def prepare_download_location():
    global videos_dir, audios_dir, playlists_dir
    downloads_folder = path.join(path.expanduser("~"), "Downloads")
    base_dir = path.join(downloads_folder, "YouTube Downloads")
    videos_dir = path.join(base_dir, "Videos")
    audios_dir = path.join(base_dir, "Audios")
    playlists_dir = path.join(base_dir, "Playlists")
    download_dirs = [base_dir, videos_dir, audios_dir, playlists_dir]
    for directory in download_dirs:
        if not path.exists(directory):
            makedirs(directory)
