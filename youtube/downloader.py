# youtube/downloader.py
# --------------------------------------------------
# Téléchargement persistant des vidéos YouTube
# - Cache local
# - Pas de doublon
# - 1 seul fichier vidéo exploitable (audio inclus)
# --------------------------------------------------

import os
import subprocess

BASE_DIR = os.path.join("storage", "videos")


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def download_video_cached(video_id: str) -> str:
    """
    Télécharge une vidéo YouTube UNE SEULE FOIS
    - Pas de doublon
    - Format unique MP4 (audio inclus)
    Retourne le chemin du fichier vidéo
    """

    ensure_dir(BASE_DIR)

    video_dir = os.path.join(BASE_DIR, video_id)
    video_path = os.path.join(video_dir, "video.mp4")

    # ✅ Cache : déjà téléchargée
    if os.path.exists(video_path):
        print("DEBUG ▶ Vidéo déjà présente :", video_path)
        return video_path

    print("DEBUG ▶ Téléchargement vidéo YouTube…")
    ensure_dir(video_dir)

    url = f"https://www.youtube.com/watch?v={video_id}"

    # ⚠️ FORMAT UNIQUE → PAS DE MERGE → PAS DE PROBLÈME FFMPEG
    cmd = [
        "python",
        "-m", "yt_dlp",
        "-f", "mp4",              # ✅ UN SEUL FORMAT
        "-o", video_path,
        url
    ]

    result = subprocess.run(cmd)

    if result.returncode != 0:
        raise RuntimeError("Téléchargement yt-dlp échoué")

    if not os.path.exists(video_path):
        raise RuntimeError("Fichier vidéo introuvable après téléchargement")

    print("DEBUG ▶ Vidéo sauvegardée :", video_path)
    return video_path
