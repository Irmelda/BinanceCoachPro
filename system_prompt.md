# 🚀 BinanceCoach Pro — Guide d'installation Windows

## Étape 1 : Installer Python
1. Va sur https://python.org/downloads
2. Télécharge Python 3.11 ou plus récent
3. **IMPORTANT** : Coche "Add Python to PATH" lors de l'installation
4. Clique "Install Now"

## Étape 2 : Créer le bot Telegram
1. Ouvre Telegram et cherche **@BotFather**
2. Envoie `/newbot`
3. Donne un nom : `BinanceCoach Pro`
4. Donne un username : `BinanceCoachProBot` (ou similaire)
5. Copie le **token** qu'il te donne (ex: `7123456789:AAHx...`)
6. Ouvre le fichier `.env` et colle le token dans `TELEGRAM_TOKEN=`

## Étape 3 : Remplir le fichier .env
Ouvre `.env` avec le Bloc-notes et remplace les valeurs :

```
TELEGRAM_TOKEN=COLLE_TON_TOKEN_TELEGRAM_ICI
ANTHROPIC_API_KEY=COLLE_TA_CLE_CLAUDE_ICI
CMC_API_KEY=COLLE_TA_CLE_CMC_ICI
X_BEARER_TOKEN=COLLE_TON_BEARER_TOKEN_X_ICI
```

## Étape 4 : Installer les dépendances
1. Ouvre le dossier `BinanceCoachPro` dans l'Explorateur
2. Clique dans la barre d'adresse, tape `cmd` et appuie sur Entrée
3. Dans le terminal qui s'ouvre, tape :

```
pip install -r requirements.txt
```

## Étape 5 : Lancer le bot
Dans le même terminal, tape :

```
python main.py
```

Tu devrais voir : `🤖 BinanceCoach Pro est en ligne !`

## Étape 6 : Tester le bot
1. Ouvre Telegram
2. Cherche ton bot par son username
3. Envoie `/start`
4. Le menu devrait apparaître ! ✅

---

## ⚠️ Problèmes courants

**"python n'est pas reconnu"**
→ Réinstalle Python en cochant "Add to PATH"

**"Module not found"**
→ Relance `pip install -r requirements.txt`

**Le bot ne répond pas**
→ Vérifie que le terminal affiche "en ligne" et que le token Telegram est correct
