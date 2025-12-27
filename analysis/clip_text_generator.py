# analysis/clip_text_generator.py
# --------------------------------------------------
# Génération de texte optimisé pour clips
# (rétention max, emojis, modifiable à la main)
# --------------------------------------------------

def generate_clip_text(
    intensity: float,
    verdict_label: str,
    category: str
) -> str:
    """
    Génère un texte court pour TikTok / Snap
    (hook + émotion + CTA léger)
    """

    # Sécurisation des entrées (MINIMUM)
    category = (category or "").upper()
    verdict_label = verdict_label or ""

    # --------------------
    # HOOK PRINCIPAL
    # --------------------
    if intensity >= 4:
        hook = "ATTENDS LA FIN 😳"
    elif intensity >= 3:
        hook = "TU VAS PAS T’Y ATTENDRE 🔥"
    else:
        hook = "PERSONNE S’ATTENDAIT À ÇA 👀"

    # --------------------
    # BONUS BUZZ
    # --------------------
    if verdict_label == "🔥 ÇA BUZZ":
        hook += " (ÇA EXPLOSE)"

    # --------------------
    # EMOJIS PAR CATÉGORIE
    # --------------------
    if "ADVENTURE" in category or "CHALLENGE" in category:
        emojis = "🔥🏕️😱"
    elif "REACTION" in category or "ENTERTAINMENT" in category:
        emojis = "😂😳🎭"
    elif "BUSINESS" in category or "MINDSET" in category:
        emojis = "🧠💸📈"
    elif "LIFESTYLE" in category or "LUXE" in category:
        emojis = "💎🚗✨"
    else:
        emojis = "👀🎬🔥"

    # --------------------
    # CTA LÉGER
    # --------------------
    cta = "👉 Dis-moi ce que t’en penses"

    # --------------------
    # TEXTE FINAL (.txt)
    # --------------------
    text = (
        f"{emojis}\n\n"
        f"{hook}\n\n"
        f"{cta}\n\n"
        f"#fyp #viral #buzz #shorts"
    )

    return text
