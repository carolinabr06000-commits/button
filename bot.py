import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# --- Config & sécurité ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("Erreur: BOT_TOKEN manquant (configurez le secret GitHub Actions).")

WELCOME_IMAGE = os.getenv("WELCOME_IMAGE")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://example.com")
LINK_PRINCIPAL = os.getenv("LINK_PRINCIPAL", "https://example.com")
LINK_SECOURS = os.getenv("LINK_SECOURS", "https://example.com")
LINK_FEEDBACK = os.getenv("LINK_FEEDBACK", "https://example.com")
INFO_IMAGE = os.getenv("INFO_IMAGE")

# --- Helpers ---
def build_links_inline():
    keyboard = [
        [InlineKeyboardButton("🌐 Principal", url=LINK_PRINCIPAL)],
        [InlineKeyboardButton("🔗 Secours", url=LINK_SECOURS)],
        [InlineKeyboardButton("📢 Feedback", url=LINK_FEEDBACK)],
        [InlineKeyboardButton("ℹ️ Informations", callback_data="info")],
    ]
    return InlineKeyboardMarkup(keyboard)

async def safe_reply_photo(msg, url: str, *, caption=None, reply_markup=None):
    """Essaye d’envoyer une photo, sinon envoie un texte"""
    try:
        if not url or "..." in url:
            raise ValueError("Invalid or empty image URL")
        await msg.reply_photo(photo=url, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        logger.warning("Photo indisponible (%s). Envoi du texte.", e)
        text = (caption or "Informations") + "\n\n(📷 Image indisponible)"
        await msg.reply_text(text, reply_markup=reply_markup, disable_web_page_preview=True)

# --- Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply_photo(
        update.message,
        WELCOME_IMAGE,
        caption="Bienvenue Chez 🏢BALTIMORE COFFEE 06🏢✨",
        reply_markup=build_links_inline(),
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "info":
        await safe_reply_photo(query.message, INFO_IMAGE, caption="Informations & Livraison")

# --- Main ---
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))

    # Debug: log tous les messages reçus
    async def echo_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
        logger.info("Message reçu: %s", update.effective_message.text)

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_debug))

    logger.info("Bot démarré, connexion à Telegram (polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()
