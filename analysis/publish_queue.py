# analysis/publish_queue.py
# --------------------------------------------------
# Gestion de la queue de publication (JSON)
# - Ajout de clips
# - Évitement des doublons
# - Changement de statut
# --------------------------------------------------

import json
import os
from datetime import datetime

QUEUE_PATH = os.path.join("storage", "publish_queue.json")


def _load_queue():
    if not os.path.exists(QUEUE_PATH):
        return {"clips": []}

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _save_queue(queue):
    os.makedirs(os.path.dirname(QUEUE_PATH), exist_ok=True)
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(queue, f, indent=2, ensure_ascii=False)


def clip_exists(clip_id: str) -> bool:
    queue = _load_queue()
    return any(c["id"] == clip_id for c in queue["clips"])


def add_clip_to_queue(
    clip_id: str,
    clip_path: str,
    caption_path: str,
    creator: str,
    video_id: str,
    moment_sec: int,
    platforms=None,
):
    if platforms is None:
        platforms = ["tiktok", "snap"]

    queue = _load_queue()

    if clip_exists(clip_id):
        return False  # déjà présent

    queue["clips"].append({
        "id": clip_id,
        "clip_path": clip_path,
        "caption_path": caption_path,
        "creator": creator,
        "video_id": video_id,
        "moment_sec": moment_sec,
        "platforms": platforms,
        "status": "pending",
        "edited": False,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "approved_at": None,
        "posted_at": None,
    })

    _save_queue(queue)
    return True


def update_clip_status(clip_id: str, status: str):
    queue = _load_queue()

    for clip in queue["clips"]:
        if clip["id"] == clip_id:
            clip["status"] = status

            if status == "approved":
                clip["approved_at"] = datetime.now().isoformat(timespec="seconds")
            if status == "posted":
                clip["posted_at"] = datetime.now().isoformat(timespec="seconds")

            _save_queue(queue)
            return True

    return False


def mark_caption_edited(clip_id: str):
    queue = _load_queue()

    for clip in queue["clips"]:
        if clip["id"] == clip_id:
            clip["edited"] = True
            _save_queue(queue)
            return True

    return False


def get_clips_by_status(status: str):
    queue = _load_queue()
    return [c for c in queue["clips"] if c["status"] == status]
