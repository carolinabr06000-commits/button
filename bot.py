
import os
import logging
from typing import Optional
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# ------------------ Config & sécurité ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("Erreur: BOT_TOKEN manquant (configurez le secret GitHub Actions).")

WELCOME_IMAGE = os.getenv("WELCOME_IMAGE")
INFO_IMAGE = os.getenv("INFO_IMAGE")

# Liens (peuvent être vides, on filtrera)
LINK_PRINCIPAL = os.getenv("LINK_PRINCIPAL")
LINK_SECOURS = os.getenv("LINK_SECOURS")
LINK_FEEDBACK = os.getenv("LINK_FEEDBACK")

# ------------------ Helpers ------------------
def _safe_url(u: Optional[str]) -> Optional[str]:
    """Retourne l'URL si valide (http/https), sinon None."""
    if not u:
        return None
    u = u.strip()
    if u.startswith("http://") or u.startswith("https://"):
        return u
    return None

def build_links_inline() -> InlineKeyboardMarkup:
    """Construit un clavier inline en n'ajoutant que des boutons valides."""
    rows = []

    p = _safe_url(LINK_PRINCIPAL)
    s = _safe_url(LINK_SECOURS)
    f = _safe_url(LINK_FEEDBACK)

    if p:
        rows.append([InlineKeyboardButton("🌐 Principal", url=p)])
    if s:
        rows.append([InlineKeyboardButton("🔗 Secours", url=s)])
    if f:
        rows.append([InlineKeyboardButton("📢 Feedback", url=f)])

    # Toujours au moins un bouton callback valide
    rows.append([InlineKeyboardButton("ℹ️ Informations", callback_data="info")])

    return InlineKeyboardMarkup(rows)

async def safe_reply_photo(msg, url: Optional[str], *, caption=None, reply_markup=None):
    """Essaye d’envoyer une photo ; si l’URL est vide/invalide ou que Telegram refuse,
    envoie un texte à la place (sans planter)."""
    try:
        if not url or "..." in url or not _safe_url(url):
            raise ValueError("Invalid or empty image URL")
        await msg.reply_photo(photo=url, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        logger.warning("Photo indisponible (%s). Envoi du texte.", e)
        text = (caption or "Informations") + "\n\n(📷 Image indisponible)"
        await msg.reply_text(text, reply_markup=reply_markup, disable_web_page_preview=True)

# ------------------ Handlers ------------------
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

# (optionnel) Debug: voir les messages texte dans les logs
async def echo_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Message reçu: %s", update.effective_message.text)

# ------------------ Main ------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_debug))

    logger.info("Bot démarré, connexion à Telegram (polling)...")
    app.run_polling()

if __name__ == "__main__":
    main()
