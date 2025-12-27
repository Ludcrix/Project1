# analysis/clip_generator.py
# --------------------------------------------------
# Génération automatique de clips verticaux
# - Format 9:16 (Snap / TikTok)
# - Recadrage centré
# - Durée contrôlée
# --------------------------------------------------

import os
import subprocess

# ✅ FFmpeg préchargé (Windows-safe)
FFMPEG = r"C:\buzz_detector\ffmpeg\bin\ffmpeg.exe"

OUTPUT_DIR = os.path.join("storage", "clips")


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def generate_vertical_clip(
    video_path: str,
    output_path: str,
    start_sec: int,
    end_sec: int
):
    """
    Génère un clip vertical 9:16 (1080x1920)
    """
    ensure_dir(os.path.dirname(output_path))

    duration = end_sec - start_sec

    cmd = [
        FFMPEG,
        "-y",
        "-ss", str(start_sec),
        "-i", video_path,
        "-t", str(duration),

        # 🎯 recadrage vertical centré
        "-vf",
        "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",

        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-c:a", "aac",
        "-b:a", "128k",

        output_path
    ]

    subprocess.run(cmd, check=True)
