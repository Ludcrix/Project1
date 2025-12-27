import os
import subprocess
import shutil

FFMPEG = shutil.which("ffmpeg")

if not FFMPEG:
    raise RuntimeError("ffmpeg introuvable")


def export_clip(
    video_path: str,
    output_path: str,
    start_sec: int,
    end_sec: int
):
    """
    Découpe + recadre en vertical (9:16) pour TikTok / Snap
    """
    duration = end_sec - start_sec

    cmd = [
        FFMPEG,
        "-y",
        "-ss", str(start_sec),
        "-i", video_path,
        "-t", str(duration),

        # 🔥 crop vertical centré
        "-vf",
        "crop=ih*9/16:ih:(iw-ih*9/16)/2:0,scale=1080:1920",

        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        "-c:a", "aac",
        "-b:a", "128k",

        output_path
    ]

    subprocess.run(cmd, check=True)
