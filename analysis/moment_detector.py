# analysis/moment_detector.py
# --------------------------------------------------
# Rôle :
# - Détecter les meilleurs moments d'une vidéo
# - Basé uniquement sur les commentaires YouTube
# - Multi-langues (émotions + timestamps)
# - Produit des timecodes exploitables humainement
# --------------------------------------------------

import re
from typing import List, Dict, Optional


# ======================
# CONSTANTES GLOBALES
# ======================

# Emojis universels = réactions humaines fortes
STRONG_EMOJIS = [
    "😂", "🤣", "😱", "🤯", "😭", "🔥", "💀", "❤️",
    "🤮", "😨", "😮", "😲", "😡", "👏"
]

# Regex timestamp (ex: 12:34 ou 1:02:45)
TIMESTAMP_REGEX = re.compile(r"\b(\d{1,2}:)?\d{1,2}:\d{2}\b")


# ======================
# UTILITAIRES
# ======================

def timestamp_to_seconds(ts: str) -> int:
    """
    Convertit un timestamp texte en secondes
    Ex:
      12:34   -> 754
      1:02:45 -> 3765
    """
    parts = [int(p) for p in ts.split(":")]

    if len(parts) == 2:
        minutes, seconds = parts
        return minutes * 60 + seconds

    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 3600 + minutes * 60 + seconds

    return 0


def has_repetition(text: str) -> bool:
    """
    Détecte les répétitions émotionnelles :
    looooool, omg!!!!, wtf?????
    """
    return bool(re.search(r"(.)\1{3,}", text))


# ======================
# ANALYSE D'UN COMMENTAIRE
# ======================

def score_comment(comment_text: str) -> Optional[Dict]:
    """
    Analyse un commentaire et retourne un score
    si le commentaire indique un moment fort
    """
    if not comment_text:
        return None

    text_lower = comment_text.lower()
    score = 0
    signals = []

    # 1️⃣ Timestamp explicite → signal le PLUS fort
    timestamps = TIMESTAMP_REGEX.findall(comment_text)
    if timestamps:
        score += 50
        signals.append("timestamp")

    # 2️⃣ Emojis forts (universels)
    emoji_count = sum(1 for e in STRONG_EMOJIS if e in comment_text)
    if emoji_count > 0:
        score += 10 * emoji_count
        signals.append("emoji")

    # 3️⃣ Ponctuation excessive
    if "!!!" in comment_text or "???" in comment_text:
        score += 10
        signals.append("punctuation")

    # 4️⃣ Répétitions de caractères
    if has_repetition(text_lower):
        score += 10
        signals.append("repetition")

    # Si aucun signal → on ignore
    if score == 0:
        return None

    return {
        "score": score,
        "signals": signals,
        "timestamps": timestamps,
        "excerpt": comment_text[:120]
    }


# ======================
# DÉTECTION DES MEILLEURS MOMENTS
# ======================

def detect_best_moments(
    comments: List[Dict],
    min_score: int = 30,
    max_results: int = 5
) -> List[Dict]:
    """
    Analyse une liste de commentaires YouTube
    et retourne les meilleurs moments détectés
    """

    detected_moments = []

    for comment in comments:
        text = comment.get("text", "")
        analysis = score_comment(text)

        if not analysis:
            continue

        if analysis["score"] < min_score:
            continue

        # Chaque timestamp devient un moment candidat
        for ts in analysis["timestamps"]:
            seconds = timestamp_to_seconds(ts)

            detected_moments.append({
                "timestamp_text": ts,
                "timestamp_sec": seconds,
                "score": analysis["score"],
                "signals": analysis["signals"],
                "comment_excerpt": analysis["excerpt"]
            })

    # Tri par pertinence décroissante
    detected_moments.sort(
        key=lambda x: (x["score"], x["timestamp_sec"]),
        reverse=True
    )

    return detected_moments[:max_results]
