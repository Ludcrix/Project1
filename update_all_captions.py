import json
import os
from datetime import datetime

from analysis.clip_text_generator import generate_clip_text

QUEUE_PATH = os.path.join("storage", "publish_queue.json")


def main():
    if not os.path.exists(QUEUE_PATH):
        print("❌ publish_queue.json introuvable")
        return

    with open(QUEUE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    clips = data.get("clips", [])
    print(f"🔄 Mise à jour de {len(clips)} captions…")

    updated = 0

    for clip in clips:
        caption_path = clip.get("caption_path")

        if not caption_path:
            print("⚠️ clip sans caption_path, skip")
            continue

        # Sécurité chemin
        caption_path = os.path.normpath(caption_path)

        # Données nécessaires
        intensity = clip.get("intensity", 3)
        verdict = clip.get("verdict_label", "🟡 BONNE VIDÉO")
        category = clip.get("category", "GENERAL CREATOR")

        # Génération du nouveau texte
        new_text = generate_clip_text(
            intensity=intensity,
            verdict_label=verdict,
            category=category
        )

        # Écriture
        os.makedirs(os.path.dirname(caption_path), exist_ok=True)
        with open(caption_path, "w", encoding="utf-8") as f:
            f.write(new_text)

        clip["edited"] = True
        clip["updated_at"] = datetime.utcnow().isoformat()
        updated += 1

        print(f"✏️ MAJ caption → {caption_path}")

    # Sauvegarde JSON
    with open(QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\n✅ {updated} captions mises à jour avec succès")


if __name__ == "__main__":
    main()
