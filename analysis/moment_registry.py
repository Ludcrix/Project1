# analysis/moment_registry.py
# ------------------------------------
# Rôle :
# - Gérer les moments déjà traités
# - Éviter les doublons
# ------------------------------------

import json
import os
from datetime import datetime

DATA_FILE = "data/processed_moments.json"


def load_registry() -> dict:
    if not os.path.exists(DATA_FILE):
        return {}
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_registry(registry: dict):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(registry, f, indent=2)


def build_moment_id(video_id: str, timestamp_sec: int) -> str:
    """
    Crée un ID stable pour un moment
    (fenêtre de 10 secondes)
    """
    bucket = timestamp_sec // 10
    return f"{video_id}_{bucket}"


def is_moment_processed(video_id: str, timestamp_sec: int) -> bool:
    registry = load_registry()
    moment_id = build_moment_id(video_id, timestamp_sec)
    return moment_id in registry


def mark_moment_processed(
    video_id: str,
    timestamp_sec: int,
    platform: str = "snap"
):
    registry = load_registry()
    moment_id = build_moment_id(video_id, timestamp_sec)

    if moment_id not in registry:
        registry[moment_id] = {
            "video_id": video_id,
            "timestamp_sec": timestamp_sec,
            "platforms": [platform],
            "created_at": datetime.utcnow().isoformat()
        }
    else:
        if platform not in registry[moment_id]["platforms"]:
            registry[moment_id]["platforms"].append(platform)

    save_registry(registry)
