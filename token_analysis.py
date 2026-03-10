"""
Skill : X Feed + Binance Announcements
Surveille les tweets Binance et les annonces officielles
"""

import requests
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()

X_BEARER_TOKEN = os.getenv("X_BEARER_TOKEN")
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Comptes Binance officiels sur X
BINANCE_X_ACCOUNTS = [
    "Binance",
    "BinanceResearch", 
    "BinanceLabs",
    "BinanceAcademy",
]

BINANCE_USER_IDS = {
    "Binance": "877807935",
    "BinanceResearch": "1052682434874789888",
}

def get_latest_tweets(username: str, max_results: int = 5) -> list:
    """Récupère les derniers tweets d'un compte Binance"""
    headers = {"Authorization": f"Bearer {X_BEARER_TOKEN}"}
    
    try:
        # Récupérer l'ID utilisateur
        user_url = f"https://api.twitter.com/2/users/by/username/{username}"
        user_resp = requests.get(user_url, headers=headers, timeout=5).json()
        user_id = user_resp.get("data", {}).get("id")

        if not user_id:
            return []

        # Récupérer les tweets récents
        tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets"
        params = {
            "max_results": max_results,
            "tweet.fields": "created_at,text",
            "exclude": "retweets,replies"
        }
        tweets_resp = requests.get(tweets_url, headers=headers, params=params, timeout=5).json()
        
        return tweets_resp.get("data", [])
    except Exception:
        return []


def get_binance_announcements() -> list:
    """Récupère les annonces officielles Binance via leur API publique"""
    try:
        response = requests.get(
            "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
            params={
                "type": 1,
                "pageNo": 1,
                "pageSize": 5
            },
            timeout=5
        )
        data = response.json()
        articles = data.get("data", {}).get("articles", [])
        return [{"title": a.get("title"), "url": f"https://www.binance.com/en/support/announcement/{a.get('code')}"} for a in articles]
    except Exception:
        return []


def get_news_summary(user_lang: str = "fr") -> str:
    """Résume les dernières news Binance avec Claude"""
    
    # Récupérer tweets
    tweets = get_latest_tweets("Binance", max_results=5)
    
    # Récupérer annonces officielles
    announcements = get_binance_announcements()

    tweet_texts = "\n".join([f"- {t.get('text', '')[:200]}" for t in tweets]) if tweets else "Aucun tweet récupéré"
    announcement_texts = "\n".join([f"- {a['title']}" for a in announcements]) if announcements else "Aucune annonce récupérée"

    prompt = f"""Tu es un assistant crypto spécialisé Binance.

Voici les derniers tweets de @Binance :
{tweet_texts}

Voici les dernières annonces officielles Binance :
{announcement_texts}

Réponds en {user_lang}. Résume les informations importantes en te concentrant sur :
1. 🆕 Nouvelles features ou produits
2. 🪂 Airdrops ou distributions de tokens
3. 💰 Opportunités APY bonus, staking, Launchpool
4. 📢 Campagnes ou événements importants
5. ⚠️ Alertes ou changements importants

Sois concis et clair. Si une info semble être une opportunité, mets-la en avant."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    summary = response.content[0].text

    lines = [
        "🐦 **Dernières News Binance**",
        "━━━━━━━━━━━━━━━━━━",
        summary,
        "",
        "🔗 _Source : @Binance + annonces officielles_",
        "⏰ _Mis à jour en temps réel_"
    ]

    return "\n".join(lines)
