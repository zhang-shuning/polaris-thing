'''This file allows for saving of maps'''

import json
import pathlib

#Don't think this game is worth putting in appdata
MAP_FOLDER_PATH = pathlib.Path("./maps")
LATEST_PATH = MAP_FOLDER_PATH / "latest_map.dat"

def ensure_save_folder_exists():
    pathlib.Path.mkdir(MAP_FOLDER_PATH, exist_ok=True)
    if not (LATEST_PATH).exists():
        with open(LATEST_PATH, "w", encoding="utf-8")as f:
            f.write("1")

def write_map(map:list[tuple[str, tuple[int]]], number = -1):
    ensure_save_folder_exists()
    if number < 0:
        with open(LATEST_PATH, "r+", encoding="utf-8") as f:
            number = f.read()
            f.seek(0)
            f.write(str(int(number)+1))
    with open(MAP_FOLDER_PATH / f"map{number}.json", "w") as f:
        f.write(json.dumps(map, indent=4, separators=(',', ': ')))

def read_map(number):
    ensure_save_folder_exists()
    if not (MAP_FOLDER_PATH / f"map{number}.json").exists():
        return None
    else:
        with open(MAP_FOLDER_PATH / f"map{number}.json", "r", encoding="utf-8") as f:
            return json.load(f)

if __name__== "__main__":
    print(read_map(2))
