# add additional lib to path
import sys
from os import path

lib_dir = path.dirname(__file__)

sys.path.append(lib_dir)
sys.path.append(path.join(lib_dir, "pytube"))
sys.path.append(path.join(lib_dir, "threads"))
sys.path.append(path.join(lib_dir, "windows"))
