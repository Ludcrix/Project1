CATEGORY_VIBE = {
    "ADVENTURE": {
        "tension": [
            "C’est là que tout a failli basculer 😳",
            "Ils ne savaient pas si ça allait passer…",
            "À ce moment précis, tout pouvait s’arrêter.",
        ],
        "question": "Tu aurais tenu jusqu’au bout ?"
    },
    "CHALLENGE": {
        "tension": [
            "Peu de gens auraient été capables de faire ça.",
            "C’est là que le mental fait la différence.",
            "Tout se joue ici.",
        ],
        "question": "Tu aurais réussi ?"
    },
    "REACTION": {
        "tension": [
            "La réaction est complètement folle 😭",
            "Personne ne s’attendait à ça.",
            "Regarde bien sa tête…",
        ],
        "question": "T’aurais réagi comment ?"
    },
    "LIFESTYLE": {
        "tension": [
            "Ce moment dit beaucoup plus qu’on le croit.",
            "C’est plus profond que ça en a l’air.",
            "Peu de gens parlent de ça.",
        ],
        "question": "T’en penses quoi ?"
    },
    "BUSINESS": {
        "tension": [
            "C’est exactement là que tout a changé.",
            "Cette décision a tout déclenché.",
            "Peu de gens comprennent ça.",
        ],
        "question": "Tu ferais pareil ?"
    },
    "MINDSET": {
        "tension": [
            "C’est là que le déclic se fait.",
            "Ce moment peut vraiment changer ta vision.",
            "Tout est une question de mental.",
        ],
        "question": "T’es d’accord avec lui ?"
    },
    "OPINION": {
        "tension": [
            "Cette opinion divise énormément.",
            "Beaucoup ne seront pas d’accord.",
            "Ça risque de faire débat.",
        ],
        "question": "Tu valides ou pas ?"
    },
    "ENTERTAINMENT": {
        "tension": [
            "Ça part complètement en vrille 😭",
            "Personne n’avait vu ça venir.",
            "Ce moment est trop drôle.",
        ],
        "question": "T’as ri toi aussi ?"
    },
}

import random


def generate_clip_caption_retention(
    verdict_label: str,
    category: str,
    intensity: float,
    clip_score: float,
):
    # 🧠 catégorie racine (avant /)
    root_category = category.split("/")[0].strip().upper()

    vibe = CATEGORY_VIBE.get(root_category)

    # Fallback safe (au cas où)
    if not vibe:
        tension = "Regarde bien ce qui se passe 👀"
        question = "Attends la fin."
    else:
        tension = random.choice(vibe["tension"])
        question = vibe["question"]

    # 🔥 Ajustement selon intensité / buzz
    if intensity > 0.85 or clip_score > 80:
        tension = tension.upper()

    # 🔁 CTA implicite
    if verdict_label == "🔥 ÇA BUZZ":
        cta = "Ne swipe pas."
    else:
        cta = "Attends la fin."

    return f"{tension}\n{question}\n{cta}"
