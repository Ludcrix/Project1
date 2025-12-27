# main.py
# ==================================================
# SCAN DE CHAÎNES YOUTUBE
# - Calcul du buzz
# - Verdict humain compréhensible
# - Filtrage logique (on ignore le non-buzz)
# - Catégorisation uniquement si utile
# - Classement final par INTÉRÊT RÉEL
# - Détection AUDIO des moments forts
# - Création automatique de clips verticaux (TikTok)
# - Génération automatique de CAPTIONS (rétention max)
# ==================================================

import os
import traceback

from analysis.audio_moment_detector import detect_audio_moments
from youtube.downloader import download_video_cached

from youtube.collector import (
    get_channel_id_by_name,
    get_channel_videos,
    get_video_info
)

from analysis.video_category import detect_video_category
from analysis.storage import save_video, load_videos
from analysis.buzz import (
    compute_buzz_score,
    quality_label,
    channel_average_vph,
    anomaly_label,
    human_verdict
)

# CLIPS
from analysis.clip_generator import generate_vertical_clip
from analysis.subtitles_generator import generate_subtitles
from analysis.subtitles_ass import srt_to_ass
from analysis.clip_renderer import render_final_clip
from analysis.moment_registry import (
    is_moment_processed,
    mark_moment_processed
)

# CAPTION RÉTENTION
from analysis.caption_generator import generate_clip_caption_retention

# 🆕 PUBLISH QUEUE
from analysis.publish_queue import add_clip_to_queue


# ==================================================
# CONFIGURATION
# ==================================================

CHANNELS = [
    "Inoxtag",
    "DutchElectrician",
    "Gmk",
]

MAX_VIDEOS_SCAN = 5
TOP_VIDEOS = 10
CLIP_PADDING_SEC = 25  # ±25s autour du moment fort


# ==================================================
# CLASSEMENT PAR INTÉRÊT RÉEL (VIDÉOS)
# ==================================================

def interest_rank(video: dict):
    verdict_label = video["verdict"]["label"]
    vph = video["buzz"]["views_per_hour"]
    score = video["buzz"]["score"]

    verdict_priority = {
        "🔥 ÇA BUZZ": 3,
        "⚠️ BUZZ POTENTIEL": 2,
        "🟡 BONNE VIDÉO": 1,
        "❓ PAS ASSEZ DE DONNÉES": 0,
    }

    return (
        verdict_priority.get(verdict_label, 0),
        vph,
        score
    )


# ==================================================
# SCORE CLIP
# ==================================================

def compute_clip_score(intensity: float, moment_sec: int, verdict_label: str) -> float:
    score = 0.0

    score += intensity * 10

    if moment_sec < 300:
        score += 15
    elif moment_sec < 900:
        score += 8

    if verdict_label == "🔥 ÇA BUZZ":
        score += 25
    elif verdict_label == "⚠️ BUZZ POTENTIEL":
        score += 12

    return round(score, 2)


# ==================================================
# DONNÉES HISTORIQUES
# ==================================================

historical_videos = load_videos()
useful_videos = []


# ==================================================
# SCAN DES CHAÎNES
# ==================================================

for channel_name in CHANNELS:
    print("\nSCAN DE LA CHAÎNE :", channel_name)
    print("=" * 70)

    channel_id = get_channel_id_by_name(channel_name)
    if not channel_id:
        print("❌ ERREUR : ID de chaîne introuvable")
        continue

    video_ids = get_channel_videos(channel_id, MAX_VIDEOS_SCAN)
    print("Vidéos analysées :", len(video_ids))

    for video_id in video_ids:
        info = get_video_info(video_id)
        if not info:
            continue

        # ======================
        # 1️⃣ BUZZ
        # ======================

        buzz = compute_buzz_score(info)
        info["buzz"] = buzz
        info["channel_name"] = channel_name
        info["video_id"] = video_id

        avg_vph = channel_average_vph(historical_videos, channel_name)
        status = anomaly_label(buzz["views_per_hour"], avg_vph)

        verdict = human_verdict(
            status=status,
            views_per_hour=buzz["views_per_hour"]
        )

        info["anomaly_status"] = status
        info["verdict"] = verdict

        # ======================
        # LOGS
        # ======================

        print("\n----------------------------------------")
        print("CHAÎNE            :", channel_name)
        print("TITRE             :", info["title"][:70])
        print("ÂGE VIDÉO         :", buzz["age_days"], "jours")
        print(
            "VUES / HEURE      :",
            buzz["views_per_hour"],
            "(" + quality_label(buzz["views_per_hour"], 500, 3000) + ")"
        )
        print("STATUT TECHNIQUE  :", status)
        print("VERDICT FINAL     :", verdict["label"])

        # ======================
        # 2️⃣ FILTRE LOGIQUE
        # ======================

        if verdict["label"] == "❌ PAS DE BUZZ":
            print("ACTION            : IGNORÉ (non pertinent)")
            continue

        # ======================
        # 3️⃣ CATÉGORIE
        # ======================

        category = detect_video_category(info)
        info["video_category"] = category

        print("CATÉGORIE VIDÉO   :", category)
        print("ACTION À FAIRE    :", verdict["action"])

        # ======================
        # 4️⃣ AUDIO + CLIPS
        # ======================

        if verdict["label"] in ("🔥 ÇA BUZZ", "⚠️ BUZZ POTENTIEL"):
            print("PIPELINE          : 🎧 Analyse audio des moments")

            try:
                video_path = download_video_cached(video_id)
                moments = detect_audio_moments(video_path)

                if not moments:
                    print("🎬 Aucun moment audio fort détecté")
                else:
                    scored_moments = []

                    for m in moments:
                        clip_score = compute_clip_score(
                            intensity=m["intensity"],
                            moment_sec=m["timestamp_sec"],
                            verdict_label=verdict["label"]
                        )

                        scored_moments.append({
                            "moment_sec": m["timestamp_sec"],
                            "clip_start": max(0, m["timestamp_sec"] - CLIP_PADDING_SEC),
                            "clip_end": m["timestamp_sec"] + CLIP_PADDING_SEC,
                            "clip_score": clip_score,
                            "intensity": m["intensity"],
                        })

                    scored_moments.sort(
                        key=lambda x: x["clip_score"],
                        reverse=True
                    )

                    # ======================
                    # CRÉATION DES CLIPS
                    # ======================

                    for m in scored_moments[:5]:
                        ts = m["moment_sec"]

                        clip_dir = f"storage/clips/{video_id}"
                        os.makedirs(clip_dir, exist_ok=True)

                        raw_clip = f"{clip_dir}/{video_id}_{ts}_raw.mp4"
                        srt_path = f"{clip_dir}/{video_id}_{ts}.srt"
                        ass_path = f"{clip_dir}/{video_id}_{ts}.ass"
                        final_mp4 = f"{clip_dir}/{video_id}_{ts}_tiktok.mp4"
                        caption_path = final_mp4.replace(".mp4", ".txt")

                        video_exists = os.path.exists(final_mp4)
                        caption_exists = os.path.exists(caption_path)

                        # 🎬 VIDÉO DÉJÀ EXISTANTE
                        if video_exists:
                            print(f"⏭️ Vidéo déjà existante : {final_mp4}")

                            if not caption_exists:
                                caption_text = generate_clip_caption_retention(
                                    verdict_label=verdict["label"],
                                    category=info["video_category"],
                                    intensity=m["intensity"],
                                    clip_score=m["clip_score"],
                                )

                                with open(caption_path, "w", encoding="utf-8") as f:
                                    f.write(caption_text)

                                print("📝 Caption manquante générée")

                            add_clip_to_queue(
                                clip_id=f"{video_id}_{ts}_tiktok",
                                clip_path=final_mp4,
                                caption_path=caption_path,
                                creator=channel_name,
                                video_id=video_id,
                                moment_sec=ts,
                                platforms=["tiktok", "snap"]
                            )

                            continue

                        # 🔒 PAS DE DOUBLON VIDÉO
                        if is_moment_processed(video_id, ts):
                            print(f"⏭️ Moment déjà traité ({video_id} @ {ts}s)")
                            continue

                        print(f"🎬 Génération clip TikTok : {final_mp4}")

                        generate_vertical_clip(
                            video_path,
                            raw_clip,
                            m["clip_start"],
                            m["clip_end"]
                        )

                        generate_subtitles(raw_clip, srt_path)
                        srt_to_ass(srt_path, ass_path)
                        render_final_clip(raw_clip, ass_path, final_mp4)

                        caption_text = generate_clip_caption_retention(
                            verdict_label=verdict["label"],
                            category=info["video_category"],
                            intensity=m["intensity"],
                            clip_score=m["clip_score"],
                        )

                        with open(caption_path, "w", encoding="utf-8") as f:
                            f.write(caption_text)

                        mark_moment_processed(video_id, ts, platform="tiktok")

                        add_clip_to_queue(
                            clip_id=f"{video_id}_{ts}_tiktok",
                            clip_path=final_mp4,
                            caption_path=caption_path,
                            creator=channel_name,
                            video_id=video_id,
                            moment_sec=ts,
                            platforms=["tiktok", "snap"]
                        )

                        print("🔥 Clip + caption TikTok prêts")

            except Exception:
                print("❌ ERREUR CLIP")
                traceback.print_exc()

        print("----------------------------------------")
        useful_videos.append(info)


# ==================================================
# TOP VIDÉOS GLOBALES
# ==================================================

useful_videos.sort(key=interest_rank, reverse=True)
top_global = useful_videos[:TOP_VIDEOS]

print("\nTOP", TOP_VIDEOS, "VIDÉOS GLOBALES (PAR INTÉRÊT)")
print("=" * 70)

for info in top_global:
    saved = save_video(info)

    print("\nCHAÎNE :", info["channel_name"])
    print("TITRE  :", info["title"][:70])
    print("CATÉGORIE :", info["video_category"])
    print("V/H    :", info["buzz"]["views_per_hour"])
    print("VERDICT:", info["verdict"]["label"])
    print("ACTION :", info["verdict"]["action"])
    print("SAVED  :", saved)

print("\nSCAN TERMINÉ")
