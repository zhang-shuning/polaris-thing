'''This file contains paths of files relating to settings'''

import json
import pathlib

#Don't think this game is worth putting in appdata
SAVE_FOLDER_PATH = pathlib.Path("../settings")
CONTROLS_PATH = SAVE_FOLDER_PATH / "controls"

def ensure_save_folder_exists():
    pathlib.Path.mkdir(SAVE_FOLDER_PATH, exist_ok=True)

