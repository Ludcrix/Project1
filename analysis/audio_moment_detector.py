# analysis/audio_moment_detector.py
# --------------------------------------------------
# Détection de moments forts via l'audio
# - Basée sur l'énergie sonore (RMS)
# - Indépendante de la langue
# - Ultra rapide, sans IA
# - Compatible Windows / Linux
# --------------------------------------------------

import os
import subprocess
import tempfile
import wave
import numpy as np
import shutil


# ==================================================
# CONFIGURATION FFMPEG
# ==================================================

FFMPEG_BINARY = shutil.which("ffmpeg")

if not FFMPEG_BINARY:
    FFMPEG_FALLBACK = r"C:\buzz_detector\ffmpeg\bin\ffmpeg.exe"
    if os.path.exists(FFMPEG_FALLBACK):
        FFMPEG_BINARY = FFMPEG_FALLBACK

if not FFMPEG_BINARY:
    raise RuntimeError("ffmpeg introuvable. Installe-le ou vérifie le chemin.")


# ==================================================
# CONFIG MOMENTS (AJOUT MINIMAL)
# ==================================================

MIN_GAP_SECONDS = 30   # anti-doublon
CLIP_PADDING = 25      # clip ±25s


# ==================================================
# EXTRACTION AUDIO
# ==================================================

def extract_audio(video_path: str, wav_path: str):
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"Vidéo introuvable : {video_path}")

    command = [
        FFMPEG_BINARY,
        "-y",
        "-i", video_path,
        "-vn",
        "-ac", "1",
        "-ar", "16000",
        "-f", "wav",
        wav_path
    ]

    subprocess.run(
        command,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True
    )

    if not os.path.exists(wav_path):
        raise RuntimeError("Extraction audio échouée (WAV non créé)")


# ==================================================
# CHARGEMENT AUDIO
# ==================================================

def load_audio(wav_path: str) -> np.ndarray:
    if not os.path.exists(wav_path):
        raise FileNotFoundError(f"WAV introuvable : {wav_path}")

    with wave.open(wav_path, "rb") as wf:
        frames = wf.readframes(wf.getnframes())
        audio = np.frombuffer(frames, dtype=np.int16)

    if audio.size == 0:
        raise RuntimeError("Audio vide après extraction")

    return audio


# ==================================================
# DÉTECTION DES PICS AUDIO
# ==================================================

def detect_audio_peaks(
    audio: np.ndarray,
    sample_rate: int = 16000,
    window_sec: float = 0.5,
    threshold_ratio: float = 2.5
) -> list:
    window_size = int(sample_rate * window_sec)
    energies = []

    for i in range(0, len(audio), window_size):
        window = audio[i:i + window_size]
        if window.size == 0:
            continue

        energy = np.sqrt(np.mean(window.astype(float) ** 2))
        energies.append((i, energy))

    if not energies:
        return []

    avg_energy = np.mean([e for _, e in energies])

    moments = []
    for index, energy in energies:
        if energy >= avg_energy * threshold_ratio:
            moments.append({
                "timestamp_sec": int(index / sample_rate),
                "intensity": round(energy / avg_energy, 2)
            })

    return moments


# ==================================================
# FILTRE ANTI-DOUBLONS (AJOUT)
# ==================================================

def filter_close_moments(moments: list) -> list:
    moments = sorted(moments, key=lambda m: m["intensity"], reverse=True)
    selected = []

    for m in moments:
        if all(
            abs(m["timestamp_sec"] - s["timestamp_sec"]) >= MIN_GAP_SECONDS
            for s in selected
        ):
            selected.append(m)

    return selected


# ==================================================
# API PRINCIPALE
# ==================================================

def detect_audio_moments(
    video_path: str,
    max_results: int = 5
) -> list:
    with tempfile.TemporaryDirectory() as tmp:
        wav_path = os.path.join(tmp, "audio.wav")

        extract_audio(video_path, wav_path)
        audio = load_audio(wav_path)
        raw_moments = detect_audio_peaks(audio)

    if not raw_moments:
        return []

    # 1️⃣ garder les meilleurs (anti-doublon)
    moments = filter_close_moments(raw_moments)

    # 2️⃣ limiter au top N
    moments = moments[:max_results]

    # 3️⃣ ajouter infos clip
    final = []
    for m in moments:
        ts = m["timestamp_sec"]
        final.append({
            "timestamp_sec": ts,
            "intensity": m["intensity"],
            "clip_start": max(ts - CLIP_PADDING, 0),
            "clip_end": ts + CLIP_PADDING
        })

    return final
