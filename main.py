"""
Skill : Launchpool & Launchpad Alerts
Nouvelles opportunités Binance en temps réel
"""

import requests
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_launchpool_data() -> list:
    """Récupère les projets Launchpool actifs depuis Binance"""
    try:
        response = requests.get(
            "https://launchpad.binance.com/gateway/v2/public/launchpool/project/list",
            params={"pageIndex": 1, "pageSize": 10},
            timeout=5
        )
        data = response.json()
        return data.get("data", {}).get("list", [])
    except Exception:
        return []


def get_launchpad_data() -> list:
    """Récupère les projets Launchpad depuis les annonces Binance"""
    try:
        response = requests.get(
            "https://www.binance.com/bapi/composite/v1/public/cms/article/list/query",
            params={
                "type": 1,
                "pageNo": 1,
                "pageSize": 10,
                "catalogId": "48"  # Catégorie Launchpad/Launchpool
            },
            timeout=5
        )
        data = response.json()
        return data.get("data", {}).get("articles", [])
    except Exception:
        return []


def get_opportunities(user_lang: str = "fr") -> str:
    """Résume les opportunités Launchpool/Launchpad actuelles"""

    launchpool = get_launchpool_data()
    launchpad = get_launchpad_data()

    launchpool_text = ""
    if launchpool:
        launchpool_text = "\n".join([
            f"- {p.get('projectName', 'N/A')} | Token: {p.get('rewardTokenSymbol', '?')} | Statut: {p.get('status', '?')}"
            for p in launchpool[:5]
        ])
    else:
        launchpool_text = "Données Launchpool non disponibles via API directe"

    launchpad_text = ""
    if launchpad:
        launchpad_text = "\n".join([f"- {a.get('title', '')}" for a in launchpad[:5]])
    else:
        launchpad_text = "Pas de nouveaux projets Launchpad détectés"

    prompt = f"""Tu es un expert des opportunités Binance.

Données Launchpool actuelles :
{launchpool_text}

Annonces Launchpad récentes :
{launchpad_text}

Réponds en {user_lang}. Présente les opportunités de manière claire :
1. 🌾 Launchpool actifs (staking pour gagner des tokens gratuits)
2. 🚀 Launchpad (nouveaux projets à venir)
3. 💡 Conseils pour participer (BNB staking, montants, deadlines)

Si les données sont limitées, explique comment trouver ces opportunités sur Binance.
Sois enthousiaste mais toujours avec un rappel DYOR."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    summary = response.content[0].text

    lines = [
        "📅 **Opportunités Launchpool & Launchpad**",
        "━━━━━━━━━━━━━━━━━━",
        summary,
        "",
        "🔗 _Pour participer : binance.com/launchpool_",
        "⚠️ _DYOR — Les rendements peuvent varier._"
    ]

    return "\n".join(lines)
