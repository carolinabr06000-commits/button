# bot.py
import os
import logging
from typing import Optional
from urllib.parse import urlparse

from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, Update, WebAppInfo,
    MenuButtonWebApp, MenuButtonDefault
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters,
)

# ------------------ Config & security ------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("Error: BOT_TOKEN missing.")

WELCOME_IMAGE = os.getenv("WELCOME_IMAGE")
INFO_IMAGE = os.getenv("INFO_IMAGE")

# Links (can be empty; we filter them)
LINK_PRINCIPAL = os.getenv("LINK_PRINCIPAL")
LINK_SECOURS = os.getenv("LINK_SECOURS")
LINK_FEEDBACK = os.getenv("LINK_FEEDBACK")
WEBAPP_URL = os.getenv("WEBAPP_URL")

INFO_TEXT = '📦 Horaires de Livraison 📦\n\n🕘 Prise de commande\n12h - 05h\n\n🚚 Livraison\n14h - 05h\n\n🤝 Meetup\nDisponible 24h/24h 7j/7\n\n🚚 Minimum de commande : 100€ 🎉\n(sauf zones éloignées — un autre minimum peut être demandé)\n\nℹ️ Tout savoir sur nous ℹ️\n\n👋 Bienvenue chez BaltiFamily 🏆✨\n\n✅ Large sélection de produits des 4 coins du monde.\n🍀 Menu mis à jour régulièrement.\n💎 Prix attractifs, produits premium.\n🤝 Équipe sérieuse, pro et à l’écoute.\n🙏 Merci pour votre confiance.\n\n🚚 Comment être livré 🚚\n🔒 Envoyez :\n- 🪪 Photo avec pièce d’identité\n- ✋ Photo de l’argent en main\n- 📹 Vidéo avec la date du jour\n\n⬇️ Exemple de commande ⬇️\n\n🛍 Commande : …\n🏡 Adresse : …\n📱 Téléphone : …\n\n⚠️ Commandes uniquement sur WhatsApp ou Telegram ⚠️'

# ------------------ Helpers ------------------
def _safe_url(u: Optional[str]) -> Optional[str]:
    """Return URL if valid (http/https + host), else None."""
    if not u:
        return None
    u = u.strip().strip('"').strip("'")
    try:
        p = urlparse(u)
        if p.scheme in ("http", "https") and p.netloc:
            return u
    except Exception:
        pass
    return None

def _webapp_info() -> Optional[WebAppInfo]:
    u = _safe_url(WEBAPP_URL)
    return WebAppInfo(url=u) if u else None

def build_main_inline() -> InlineKeyboardMarkup:
    """Main screen: WebApp + Info."""
    rows = []
    w = _webapp_info()
    p = _safe_url(LINK_PRINCIPAL)
    s = _safe_url(LINK_SECOURS)
    f = _safe_url(LINK_FEEDBACK)

    if w:
        rows.append([InlineKeyboardButton("🛒 Ouvrir l’app", web_app=w)])
    if p:
        rows.append([InlineKeyboardButton("🌐 Principal", url=p)])
    if s:
        rows.append([InlineKeyboardButton("🔗 Secours", url=s)])
    if f:
        rows.append([InlineKeyboardButton("📢 Feedback", url=f)])
    rows.append([InlineKeyboardButton("ℹ️ Informations", callback_data="info")])

    logger.info("Buttons (main): webapp=%s, principal=%s, secours=%s, feedback=%s",
                bool(w), bool(p), bool(s), bool(f))
    return InlineKeyboardMarkup(rows)

def build_info_inline() -> InlineKeyboardMarkup:
    """Info screen: ONLY Back (no WebApp button here)."""
    rows = []
    rows.append([InlineKeyboardButton("⬅️ Retour", callback_data="back")])
    return InlineKeyboardMarkup(rows)

async def safe_reply_photo(msg, url: Optional[str], *, caption=None, reply_markup=None):
    """Try to send photo; else send text without failing."""
    try:
        if not _safe_url(url):
            raise ValueError("Invalid or empty image URL")
        await msg.reply_photo(photo=url, caption=caption, reply_markup=reply_markup)
    except Exception as e:
        logging.getLogger(__name__).warning("Photo unavailable (%s). Sending text.", e)
        text = (caption or "Informations") + "\n\n(📷 Image indisponible)"
        await msg.reply_text(text, reply_markup=reply_markup, disable_web_page_preview=True)

async def safe_edit_message(query, *, new_caption: Optional[str], new_text: Optional[str], reply_markup):
    """Edit caption if photo, else edit text, else fallback to new message."""
    try:
        if query.message and query.message.photo:
            # Keep simple caption on photo screens
            await query.edit_message_caption(caption=new_caption or "", reply_markup=reply_markup)
            # Also send a separate text message if detailed info is provided
            if new_text and new_text != new_caption:
                await query.message.reply_text(new_text, disable_web_page_preview=True, reply_markup=reply_markup)
        else:
            await query.edit_message_text(text=new_text or "", reply_markup=reply_markup, disable_web_page_preview=True)
    except Exception as e:
        logging.getLogger(__name__).warning("Cannot edit message (%s). Sending new message.", e)
        await query.message.reply_text(new_text or new_caption or "Informations", reply_markup=reply_markup, disable_web_page_preview=True)

# ------------------ Handlers ------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await safe_reply_photo(
        update.message,
        WELCOME_IMAGE,
        caption="Bienvenue Chez 🏢BALTIMORE COFFEE 06🏢✨",
        reply_markup=build_main_inline(),
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "info":
        # Send compact caption on the original message + full text as a new message
        caption = "Informations & Livraison"
        await safe_edit_message(query, new_caption=caption, new_text=INFO_TEXT, reply_markup=build_info_inline())
    elif query.data == "back":
        caption = "Bienvenue Chez 🏢BALTIMORE COFFEE 06🏢✨"
        await safe_edit_message(query, new_caption=caption, new_text=caption, reply_markup=build_main_inline())

async def echo_debug(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("Message reçu: %s", update.effective_message.text)

# ------------------ Main ------------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    async def _startup(application: Application):
        await application.bot.delete_webhook(drop_pending_updates=True)
        w = _webapp_info()
        try:
            if w:
                await application.bot.set_chat_menu_button(menu_button=MenuButtonWebApp(text="🛒 Ouvrir l’app", web_app=w))
                logger.info("MenuButtonWebApp configured")
            else:
                await application.bot.set_chat_menu_button(menu_button=MenuButtonDefault())
                logger.info("MenuButton reset (no WEBAPP_URL)")
        except Exception as e:
            logger.warning("Cannot set MenuButton: %s", e)
        logger.info("Webhook deleted, using polling.")

    app.post_init = _startup

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo_debug))

    logger.info("Bot running (polling)...")
    app.run_polling(allowed_updates=Update.ALL_TYPES, poll_interval=2.0)

if __name__ == "__main__":
    main()