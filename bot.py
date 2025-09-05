import logging, os
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

# Config via variables d'environnement (garde les valeurs par défaut de ton fichier original)
BOT_TOKEN = os.getenv("BOT_TOKEN")
WELCOME_IMAGE = os.getenv("WELCOME_IMAGE", "https://image.noelshack.com/fichiers/2025/36/5/1757064326-design-sans-titre-1.png")
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://jovial-puffpuff-f0e4f9.netlify.app/")
LINK_PRINCIPAL = os.getenv("LINK_PRINCIPAL", "https://t.me/BALTIMORE06")
LINK_SECOURS = os.getenv("LINK_SECOURS", "https://t.me/+_koc3vmMcKM3YmU0")
LINK_FEEDBACK = os.getenv("LINK_FEEDBACK", "https://t.me/BALTIMOREFEEDBACK")
INFO_IMAGE = os.getenv("INFO_IMAGE", "https://image.noelshack.com/fichiers/2025/36/5/1757074614-b7a2fa67-0db0-4741-ba7b-a655ec998d6b.jpg")  # Image affichée pour la section Informations

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


def build_links_inline() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("✅Principal 📺", url=LINK_PRINCIPAL)],
            [InlineKeyboardButton("⚠️Secours📺",   url=LINK_SECOURS)],
            [InlineKeyboardButton("🤖Baltimore MiniApp🤖", web_app=WebAppInfo(url=WEBAPP_URL))],
            [InlineKeyboardButton("ℹ️Informationsℹ️", callback_data="info")],
            [InlineKeyboardButton("💙Retour Clients💙", url=LINK_FEEDBACK)],
        ]
    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Affiche la photo de bienvenue ET les boutons inline directement sous la photo
    await update.message.reply_photo(
        photo=WELCOME_IMAGE,
        caption="Bienvenue Chez 🏢BALTIMORE COFFEE 06🏢✨",
        reply_markup=build_links_inline(),
    )


async def on_info_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # 1) Envoyer l'image seule
    await query.message.reply_photo(
        photo=INFO_IMAGE,
        caption="Informations & Livraison"
    )

    # 2) Envoyer le texte + bouton Retour en bas du texte
    details = """📦 *Horaires de Livraison* 📦

🕘 *Prise de commande*
12h - 05h

🚚 *Livraison*
14h - 05h

🤝 *Meetup*
Disponible 24h/24h 7j/7

🚚 *Minimum de commande* : 100€ 🎉
(sauf zones éloignées — un autre minimum peut être demandé)

ℹ️ *Tout savoir sur nous* ℹ️

👋 Bienvenue chez *BaltiFamily* 🏆✨

✅ Large sélection de produits des 4 coins du monde.
🍀 Menu mis à jour régulièrement.
💎 Prix attractifs, produits premium.
🤝 Équipe sérieuse, pro et à l’écoute.
🙏 Merci pour votre confiance.

🚚 *Comment être livré* 🚚
🔒 Envoyez :
- 🪪 Photo avec pièce d’identité
- ✋ Photo de l’argent en main
- 📹 Vidéo avec la date du jour

⬇️ *Exemple de commande* ⬇️

🛍 *Commande* : …
🏡 *Adresse* : …
📱 *Téléphone* : …

⚠️ *Commandes uniquement sur WhatsApp ou Telegram* ⚠️
"""
    await query.message.reply_text(
        details,
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("⬅️ Retour", callback_data="back")]]
        )
    )


async def on_back_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_photo(
        photo=WELCOME_IMAGE,
        caption="Bienvenue Chez 🏢BALTIMORE COFFEE 06🏢✨",
        reply_markup=build_links_inline(),
    )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Silence volontaire ; tout passe par les boutons inline
    return


async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    c = update.message.contact
    await update.message.reply_text(f"Merci {c.first_name} ✅\nNuméro reçu: {c.phone_number}")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error("Exception: %s", context.error)


def main():
    if not BOT_TOKEN:
        raise SystemExit("Erreur: BOT_TOKEN manquant (secret GitHub Actions requis).")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(on_info_callback, pattern="^info$"))
    app.add_handler(CallbackQueryHandler(on_back_callback, pattern="^back$"))
    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_error_handler(error_handler)
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
