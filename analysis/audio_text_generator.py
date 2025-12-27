# --------------------------------------------------
# Génération de texte overlay à partir de l'audio
# --------------------------------------------------

def generate_audio_text(category: str, intensity: float) -> str:
    category = (category or "").upper()

    # 🔥 explosions
    if intensity >= 3.5:
        if "REACTION" in category:
            return "😱 ÇA DÉGÉNÈRE"
        if "ADVENTURE" in category:
            return "ILS ÉTAIENT PAS PRÊTS"
        if "TUTORIAL" in category:
            return "❌ GROSSE ERREUR"
        return "💥 MOMENT CHOC"

    # ⚠️ réactions fortes
    if intensity >= 2.0:
        if "REACTION" in category:
            return "💀 ATTENDS LA FIN"
        if "ADVENTURE" in category:
            return "LA TENSION MONTE"
        if "TUTORIAL" in category:
            return "⚠️ REGARDE BIEN"
        return "👀 MOMENT IMPORTANT"

    # 👀 fallback
    return "👀 REGARDE CE MOMENT"
