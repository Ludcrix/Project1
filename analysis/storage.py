# analysis/storage.py
# Rôle : sauvegarder et charger les données vidéo

import json
import os

DATA_PATH = os.path.join("data", "videos.json")


def load_videos():
    if not os.path.exists(DATA_PATH):
        return []

    with open(DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_video(video_data):
    videos = load_videos()

    # éviter les doublons
    for v in videos:
        if v["video_id"] == video_data["video_id"]:
            return False

    videos.append(video_data)

    with open(DATA_PATH, "w", encoding="utf-8") as f:
        json.dump(videos, f, indent=2, ensure_ascii=False)

    return True
