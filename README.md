# Bot Telegram "Baltimore" — Déploiement GitHub Actions (gratuit)

Ce repo lance le bot via **GitHub Actions** et le **relance toutes les 5 heures**
(limite technique des jobs). Le bot est donc disponible en continu.

## ⚙️ Secrets & Variables (GitHub)
1. Allez dans `Settings > Secrets and variables > Actions` :
   - **Secrets** : `BOT_TOKEN` (obligatoire)
   - **Variables** (facultatif) :
     - `WELCOME_IMAGE` (URL de l'image d'accueil)
     - `WEBAPP_URL` (URL Netlify de la MiniApp)
     - `LINK_PRINCIPAL`, `LINK_SECOURS`, `LINK_FEEDBACK`
2. Démarrez manuellement via l'onglet **Actions** → workflow → **Run workflow**,
   ou attendez l'exécution planifiée (toutes les 5h).

## 🧪 Lancer en local
```bash
pip install -r requirements.txt
export BOT_TOKEN="TON_TOKEN"  # Windows: set BOT_TOKEN=TON_TOKEN
python bot.py
```

## ❗ Notes
- Le workflow s'exécute max ~6 heures/launch (limite GitHub). Il est replanifié toutes les 5h.
- Le bouton "Contact 📱" demande le numéro (request_contact=True).
- Le bouton "Baltimore MiniApp🤖" ouvre votre WebApp Netlify.


# Telegram Bot – Déploiement local & GitHub Actions

## Variables d'environnement requises
- `BOT_TOKEN` (secret): token du bot Telegram.
- `WEBAPP_URL` (variable): `https://jovial-puffpuff-f0e4f9.netlify.app/` (ou votre URL).
- Optionnelles: `WELCOME_IMAGE`, `INFO_IMAGE`, `LINK_PRINCIPAL`, `LINK_SECOURS`, `LINK_FEEDBACK`.

## Lancer en local
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export BOT_TOKEN="12345:ABC"
export WEBAPP_URL="https://jovial-puffpuff-f0e4f9.netlify.app/"
python bot.py
```

## GitHub Actions
Le workflow ci-dessous empêche les chevauchements via `concurrency` et peut être planifié toutes les 6h.