# analysis/buzz.py
# --------------------------------------------------
# RÔLE :
# - Calculer le buzz d'une vidéo YouTube
# - Comparer la performance à la moyenne de la chaîne
# - Fournir un verdict HUMAIN (buzz / pas buzz)
# --------------------------------------------------

from datetime import datetime, timezone
from typing import Optional


# ==================================================
# UTILITAIRES TEMPS
# ==================================================

def iso_to_datetime(iso_str: str) -> datetime:
    """
    Convertit une date ISO YouTube (ex: 2024-01-01T12:00:00Z)
    en datetime UTC Python
    """
    return datetime.fromisoformat(iso_str.replace("Z", "+00:00"))


# ==================================================
# CALCUL DU BUZZ
# ==================================================

def compute_buzz_score(video: dict) -> dict:
    """
    Calcule les indicateurs de buzz d'une vidéo
    (ne décide PAS seul, sert à comparer et trier)
    """
    now = datetime.now(timezone.utc)
    published_at = iso_to_datetime(video["published_at"])

    # Âge de la vidéo
    age_hours = max((now - published_at).total_seconds() / 3600, 1)
    age_days = round(age_hours / 24, 2)

    # Données brutes
    views = int(video.get("views", 0))
    likes = int(video.get("likes", 0))
    comments = int(video.get("comments", 0))

    # Indicateurs
    views_per_hour = views / age_hours if age_hours > 0 else 0
    like_ratio = likes / views if views > 0 else 0
    comment_ratio = comments / views if views > 0 else 0

    # Score synthétique (pour classement interne)
    score = (
        views_per_hour * 0.60 +
        like_ratio * 1000 * 0.25 +
        comment_ratio * 2000 * 0.15
    )

    return {
        "score": round(score, 2),
        "age_days": age_days,
        "views_per_hour": round(views_per_hour, 2),
        "like_ratio": round(like_ratio, 4),
        "comment_ratio": round(comment_ratio, 4),
    }


# ==================================================
# LECTURE SIMPLE DES CHIFFRES
# ==================================================

def quality_label(value: float, low: float, high: float) -> str:
    """
    Transforme un chiffre brut en lecture humaine
    """
    if value < low:
        return "faible"
    elif value < high:
        return "correct"
    else:
        return "bon"


# ==================================================
# MOYENNE DE CHAÎNE
# ==================================================

def channel_average_vph(
    videos: list,
    channel_name: str
) -> Optional[float]:
    """
    Calcule la moyenne habituelle des vues/heure
    pour une chaîne donnée
    """
    values = []

    for video in videos:
        if video.get("channel_name") != channel_name:
            continue

        buzz = video.get("buzz")
        if not buzz:
            continue

        vph = buzz.get("views_per_hour")
        if isinstance(vph, (int, float)):
            values.append(vph)

    if not values:
        return None

    return round(sum(values) / len(values), 2)


# ==================================================
# STATUT TECHNIQUE
# ==================================================

def anomaly_label(
    current_vph: float,
    avg_vph: Optional[float]
) -> str:
    """
    Compare une vidéo à la performance normale de la chaîne
    """
    if not avg_vph or avg_vph <= 0:
        return "inconnu"

    ratio = current_vph / avg_vph

    if ratio >= 2:
        return "ANOMALIE 🚨"
    elif ratio >= 1.3:
        return "au-dessus de la moyenne ⚠️"
    else:
        return "normal"


# ==================================================
# VERDICT HUMAIN FINAL (LE PLUS IMPORTANT)
# ==================================================

def human_verdict(
    status: str,
    views_per_hour: float
) -> dict:
    """
    Verdict compréhensible par un humain (business)
    """
    if status.startswith("ANOMALIE"):
        return {
            "label": "🔥 ÇA BUZZ",
            "meaning": "La vidéo explose clairement.",
            "action": "EXPORT SNAP IMMÉDIAT",
        }

    if status.startswith("au-dessus"):
        if views_per_hour >= 1500:
            return {
                "label": "⚠️ BUZZ POTENTIEL",
                "meaning": "La vidéo performe mieux que d'habitude.",
                "action": "TEST SNAP / SURVEILLER",
            }
        else:
            return {
                "label": "🟡 BONNE VIDÉO",
                "meaning": "Bonne perf mais pas prioritaire.",
                "action": "OPTIONNEL",
            }

    if status == "inconnu":
        return {
            "label": "❓ PAS ASSEZ DE DONNÉES",
            "meaning": "Pas assez d'historique pour juger.",
            "action": "ATTENDRE",
        }

    return {
        "label": "❌ PAS DE BUZZ",
        "meaning": "Aucun signal intéressant.",
        "action": "IGNORER",
    }

def acceleration_label(video_id: str, snapshots: dict):
    """
    Détecte une accélération récente du buzz
    """
    history = snapshots.get(video_id, [])

    if len(history) < 2:
        return {
            "label": "⏳ PAS ASSEZ DE DONNÉES",
            "detail": "Première mesure"
        }

    last = history[-1]
    prev = history[-2]

    prev_vph = prev["views_per_hour"]
    curr_vph = last["views_per_hour"]

    if prev_vph <= 0:
        return {
            "label": "⏳ PAS ASSEZ DE DONNÉES",
            "detail": "Base invalide"
        }

    growth = (curr_vph - prev_vph) / prev_vph

    if growth >= 1:
        return {
            "label": "🚀 ACCÉLÉRATION FORTE",
            "detail": f"+{int(growth*100)}% en peu de temps"
        }

    if growth >= 0.3:
        return {
            "label": "📈 ACCÉLÉRATION MODÉRÉE",
            "detail": f"+{int(growth*100)}%"
        }

    return {
        "label": "😴 STABLE",
        "detail": "Pas d’accélération notable"
    }
