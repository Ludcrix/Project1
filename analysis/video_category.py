# analysis/video_category.py
# --------------------------------------------------
# RÔLE :
# - Déterminer la catégorie d'une vidéo YouTube
# - Priorité : contenu de la vidéo
# - Fallback : profil global du créateur
# --------------------------------------------------

from analysis.creator_profile import detect_creator_profile


def detect_video_category(video: dict) -> str:
    """
    Retourne une catégorie claire et exploitable business
    """

    title = video.get("title", "").lower()
    channel_name = video.get("channel_name", "").lower()

    # ==================================================
    # CATÉGORIES BASÉES SUR LE CONTENU DE LA VIDÉO
    # ==================================================
    video_categories = {
        "MINDSET / MOTIVATION": [
            "mindset", "motivation", "discipline", "mental",
            "réussir", "réussite", "succès", "objectifs",
            "habitudes", "inspiration", "confiance"
        ],

        "ENTREPRENEUR / BUSINESS": [
            "business", "argent", "money", "entreprise",
            "startup", "entrepreneur", "revenu",
            "investir", "investissement", "marketing",
            "ecommerce", "dropshipping"
        ],

        "ADVENTURE / CHALLENGE": [
            "survivre", "challenge", "aventure",
            "exploration", "24h", "48h",
            "7 jours", "10 jours", "semaine"
        ],

        "TUTORIAL / HOWTO": [
            "installation", "installer", "how",
            "comment", "tuto", "tutorial",
            "guide", "brancher", "configurer"
        ],

        "REACTION / LIVE": [
            "réagit", "reaction", "live", "ft",
            "on regarde", "je réagis", "stream"
        ],

        "ANNONCE / GIVEAWAY": [
            "gagne", "donne", "cadeau", "giveaway",
            "offre", "concours", "annonce"
        ],

        "LIFESTYLE / VLOG": [
            "vlog", "routine", "journée",
            "ma vie", "quotidien", "voyage"
        ],

        "TECH / REVIEW": [
            "test", "review", "avis",
            "comparatif", "unboxing", "tech"
        ],

        "DRAMA / CLASH": [
            "clash", "drama", "embrouille",
            "fail", "scandale", "polémique"
        ],
    }

    # ==================================================
    # 1️⃣ DÉTECTION PAR LE TITRE (PRIORITAIRE)
    # ==================================================
    for category, keywords in video_categories.items():
        for keyword in keywords:
            if keyword in title:
                return category

    # ==================================================
    # 2️⃣ FALLBACK : PROFIL GLOBAL DU CRÉATEUR
    # ==================================================
    creator_category = detect_creator_profile(channel_name)

    if creator_category:
        return creator_category

    # ==================================================
    # 3️⃣ DERNIER FILET DE SÉCURITÉ
    # ==================================================
    return "GENERAL CREATOR"
