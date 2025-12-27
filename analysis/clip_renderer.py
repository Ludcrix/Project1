import subprocess
import os

# ✅ FFmpeg préchargé (Windows-safe)
FFMPEG = r"C:\buzz_detector\ffmpeg\bin\ffmpeg.exe"


def render_final_clip(video_path: str, ass_path: str, output_path: str):
    ass_path = ass_path.replace(os.sep, "/")

    cmd = [
    FFMPEG,
    "-y",

    # 🔧 RECONSTRUIT LES TIMESTAMPS
    "-fflags", "+genpts",
    "-avoid_negative_ts", "make_zero",

    "-i", video_path,
    "-vf", f"ass=filename='{ass_path}'",

    # 🎥 VIDÉO SAFE TIKTOK
    "-c:v", "libx264",
    "-profile:v", "high",
    "-level", "4.0",
    "-pix_fmt", "yuv420p",
    "-r", "30",
    "-g", "60",

    # 🔊 AUDIO REENCODÉ (IMPORTANT)
    "-c:a", "aac",
    "-b:a", "128k",

    "-movflags", "+faststart",
    output_path
]


    subprocess.run(cmd, check=True)
