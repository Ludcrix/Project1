import json
import os
from datetime import datetime, timezone

SNAPSHOT_FILE = "data/video_snapshots.json"


def load_snapshots():
    if not os.path.exists(SNAPSHOT_FILE):
        return {}
    with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_snapshots(data):
    os.makedirs("data", exist_ok=True)
    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_snapshot(video_id: str, views: int, views_per_hour: float):
    data = load_snapshots()

    now = datetime.now(timezone.utc).isoformat()

    entry = {
        "timestamp": now,
        "views": views,
        "views_per_hour": views_per_hour
    }

    if video_id not in data:
        data[video_id] = []

    data[video_id].append(entry)

    # On garde seulement les 10 derniers points
    data[video_id] = data[video_id][-10:]

    save_snapshots(data)
