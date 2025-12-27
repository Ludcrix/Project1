# analysis/clip_scoring.py
# --------------------------------------------------
# Score final d’un CLIP (pas de la vidéo)
# --------------------------------------------------

def compute_clip_score(
    audio_intensity: float,
    moment_sec: int,
    video_verdict_label: str
) -> float:
    """
    Score final pour prioriser un clip
    """

    score = 0.0

    # 1️⃣ Intensité audio (signal principal)
    score += audio_intensity * 10

    # 2️⃣ Bonus si moment tôt dans la vidéo
    if moment_sec < 300:
        score += 15
    elif moment_sec < 900:
        score += 8

    # 3️⃣ Bonus si vidéo très buzz
    if video_verdict_label == "🔥 ÇA BUZZ":
        score += 25
    elif video_verdict_label == "⚠️ BUZZ POTENTIEL":
        score += 12

    return round(score, 2)
