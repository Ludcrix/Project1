# telegram_bot.py
# ==================================================
# BOT TELEGRAM - VALIDATION DES CLIPS
# Python 3.14 + Windows SAFE
# VERSION STABLE + LOGS + COMPTEURS + TXT ÉDITABLE + RESTORE
# ==================================================

import json
import os
import asyncio
from datetime import datetime

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

from config import TELEGRAM_BOT_TOKEN


# ==================================================
# CONFIG
# ==================================================

PUBLISH_QUEUE_PATH = os.path.join("storage", "publish_queue.json")

# 🔥 ÉTAT TEMPORAIRE : utilisateur → clip en édition
EDITING_CLIP = {}


# ==================================================
# QUEUE UTILS
# ==================================================

def load_queue():
    print("[QUEUE] Chargement de publish_queue.json")

    if not os.path.exists(PUBLISH_QUEUE_PATH):
        print("[QUEUE][WARN] Fichier publish_queue.json introuvable")
        return []

    with open(PUBLISH_QUEUE_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and "clips" in data:
        print(f"[QUEUE] {len(data['clips'])} clips chargés")
        return data["clips"]

    if isinstance(data, list):
        print(f"[QUEUE] {len(data)} clips chargés (ancien format)")
        return data

    print("[QUEUE][ERROR] Format JSON non reconnu")
    return []


def save_queue(queue):
    print(f"[QUEUE] Sauvegarde de {len(queue)} clips")
    with open(PUBLISH_QUEUE_PATH, "w", encoding="utf-8") as f:
        json.dump({"clips": queue}, f, indent=2, ensure_ascii=False)


def get_queue_stats():
    queue = load_queue()

    total = len(queue)
    pending = sum(1 for c in queue if c.get("status") == "pending")
    approved = sum(1 for c in queue if c.get("status") == "approved")
    rejected = sum(1 for c in queue if c.get("status") == "rejected")

    print(
        f"[STATS] Total={total} | Pending={pending} | "
        f"Approved={approved} | Rejected={rejected}"
    )

    return {
        "total": total,
        "pending": pending,
        "approved": approved,
        "rejected": rejected,
    }


def get_next_pending_clip():
    queue = load_queue()
    print("[QUEUE] Recherche clip pending")

    for item in queue:
        if item.get("status") == "pending":
            print(f"[QUEUE] ▶ Clip sélectionné : {item.get('id')}")
            return item

    print("[QUEUE] Aucun clip pending")
    return None


def update_clip_status(clip_id: str, new_status: str):
    print(f"[QUEUE] Update {clip_id} → {new_status}")

    queue = load_queue()

    for item in queue:
        if item.get("id") == clip_id:
            item["status"] = new_status
            item["updated_at"] = datetime.utcnow().isoformat()

    save_queue(queue)


# ==================================================
# TELEGRAM HANDLERS
# ==================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[CMD] /start")

    stats = get_queue_stats()

    await update.message.reply_text(
        "🤖 *Bot prêt*\n\n"
        f"📊 Clips : {stats['pending']} en attente / {stats['total']} total\n\n"
        "/next → prochain clip à valider",
        parse_mode="Markdown"
    )


async def next_clip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("[CMD] /next")

    stats = get_queue_stats()
    clip = get_next_pending_clip()

    if not clip:
        await update.message.reply_text(
            f"✅ Aucun clip en attente.\n\n"
            f"📊 {stats['pending']} / {stats['total']} clips restants"
        )
        return

    video_path = os.path.normpath(clip["clip_path"])
    caption_path = os.path.normpath(clip["caption_path"])

    if not os.path.exists(video_path):
        print("[ERROR] Vidéo introuvable")
        await update.message.reply_text(f"❌ Vidéo introuvable :\n{video_path}")
        return

    caption_text = ""
    if os.path.exists(caption_path):
        with open(caption_path, "r", encoding="utf-8") as f:
            caption_text = f.read()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ MODIFIER TEXTE", callback_data=f"edit|{clip['id']}"),
            InlineKeyboardButton("↩️ TEXTE ORIGINAL", callback_data=f"restore|{clip['id']}"),
        ],
        [
            InlineKeyboardButton("✅ APPROUVER", callback_data=f"approve|{clip['id']}"),
            InlineKeyboardButton("❌ REFUSER", callback_data=f"reject|{clip['id']}"),
        ],
        [
            InlineKeyboardButton("⏸ PLUS TARD", callback_data=f"later|{clip['id']}"),
        ]
    ])

    await update.message.reply_video(
        video=open(video_path, "rb"),
        caption=(
            f"🎬 *{clip.get('creator','?')}*\n"
            f"📺 `{clip.get('video_id')}`\n"
            f"⏱ Moment : {clip.get('moment_sec')}s\n\n"
            f"{caption_text}\n\n"
            f"📊 *{stats['pending']} / {stats['total']} clips restants*"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    action, clip_id = query.data.split("|")
    print(f"[BTN] {action} sur {clip_id}")

    queue = load_queue()
    clip = None

    for item in queue:
        if item.get("id") == clip_id:
            clip = item
            break

    if not clip:
        await query.message.reply_text("❌ Erreur : clip introuvable.")
        return

    # =========================
    # MODE ÉDITION
    # =========================
    if action == "edit":
        EDITING_CLIP[query.from_user.id] = clip_id

        await query.message.reply_text(
            "✏️ *Mode édition activé*\n\n"
            "Envoie maintenant le **nouveau texte** du clip.\n"
            "Il remplacera entièrement l’ancien.",
            parse_mode="Markdown"
        )
        return

    # =========================
    # RESTORE TEXTE ORIGINAL
    # =========================
    if action == "restore":
        original = clip.get("caption_original")

        if not original:
            await query.message.reply_text("⚠️ Aucun texte original enregistré.")
            return

        with open(clip["caption_path"], "w", encoding="utf-8") as f:
            f.write(original)

        clip["caption_current"] = original
        clip["updated_at"] = datetime.utcnow().isoformat()

        save_queue(queue)

        await query.message.reply_text(
            "↩️ *Texte original restauré*\n\n"
            "Tu peux maintenant modifier ou approuver.",
            parse_mode="Markdown"
        )
        return

    # =========================
    # APPROVE / REJECT / LATER
    # =========================
    if action == "approve":
        update_clip_status(clip_id, "approved")
        msg = "✅ *Clip APPROUVÉ*\nPrêt pour publication."

    elif action == "reject":
        update_clip_status(clip_id, "rejected")
        msg = "❌ *Clip REFUSÉ*"

    else:
        msg = "⏸ *Clip remis plus tard*"

    stats = get_queue_stats()

    await query.edit_message_caption(
        f"{msg}\n\n📊 {stats['pending']} / {stats['total']} clips restants",
        parse_mode="Markdown"
    )


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id

    if user_id not in EDITING_CLIP:
        return

    clip_id = EDITING_CLIP.pop(user_id)
    print(f"[EDIT] Nouveau texte pour {clip_id}")

    queue = load_queue()
    clip = None

    for item in queue:
        if item.get("id") == clip_id:
            clip = item

            # 🔐 Sauvegarde du texte original UNE FOIS
            if "caption_original" not in item:
                with open(item["caption_path"], "r", encoding="utf-8") as f:
                    item["caption_original"] = f.read()

            item["caption_current"] = update.message.text

            with open(item["caption_path"], "w", encoding="utf-8") as f:
                f.write(update.message.text)

            item["edited"] = True
            item["updated_at"] = datetime.utcnow().isoformat()
            break

    save_queue(queue)

    if not clip:
        await update.message.reply_text("❌ Erreur : clip introuvable.")
        return

    video_path = os.path.normpath(clip["clip_path"])
    stats = get_queue_stats()

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✏️ MODIFIER TEXTE", callback_data=f"edit|{clip['id']}"),
            InlineKeyboardButton("↩️ TEXTE ORIGINAL", callback_data=f"restore|{clip['id']}"),
        ],
        [
            InlineKeyboardButton("✅ APPROUVER", callback_data=f"approve|{clip['id']}"),
            InlineKeyboardButton("❌ REFUSER", callback_data=f"reject|{clip['id']}"),
        ],
    ])

    await update.message.reply_video(
        video=open(video_path, "rb"),
        caption=(
            "✏️ *Texte mis à jour*\n\n"
            f"{update.message.text}\n\n"
            f"📊 *{stats['pending']} / {stats['total']} clips restants*"
        ),
        parse_mode="Markdown",
        reply_markup=keyboard
    )


# ==================================================
# MAIN ASYNC (STABLE)
# ==================================================

async def main_async():
    print("[BOT] Initialisation")

    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("next", next_clip))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("[BOT] Bot Telegram lancé")

    await app.initialize()
    await app.start()

    print("[BOT] Polling actif")
    await app.updater.start_polling()

    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main_async())