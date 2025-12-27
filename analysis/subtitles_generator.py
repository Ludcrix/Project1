import whisper
import os

os.environ["PATH"] += os.pathsep + r"C:\buzz_detector\ffmpeg\bin"


model = whisper.load_model("base")  # rapide + suffisant


def generate_subtitles(video_path: str, srt_path: str):
    result = model.transcribe(video_path, fp16=False)

    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"], start=1):
            start = segment["start"]
            end = segment["end"]
            text = segment["text"].strip()

            f.write(f"{i}\n")
            f.write(f"{format_ts(start)} --> {format_ts(end)}\n")
            f.write(f"{text}\n\n")


def format_ts(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = seconds % 60
    return f"{h:02}:{m:02}:{s:06.3f}".replace(".", ",")
