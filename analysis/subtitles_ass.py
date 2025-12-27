import subprocess

# ✅ FFmpeg préchargé (Windows-safe)
FFMPEG = r"C:\buzz_detector\ffmpeg\bin\ffmpeg.exe"


def srt_to_ass(srt_path: str, ass_path: str):
    subprocess.run(
        [FFMPEG, "-y", "-i", srt_path, ass_path],
        check=True
    )
