import json
import os


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def ensure_folder(path):
    if not os.path.exists(path):
        os.makedirs(path)
