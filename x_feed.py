"""
Skill : Market Movement
Explique pourquoi le marché monte ou chute
Utilise Binance API (public) + Claude pour l'analyse
"""

import requests
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

def get_market_overview() -> dict:
    """Récupère les données de marché globales depuis Binance"""
    try:
        # Top tokens pour avoir une vue d'ensemble
        top_pairs = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT"]
        market_data = []

        for pair in top_pairs:
            ticker = requests.get(
                f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}",
                timeout=5
            ).json()
            market_data.append({
                "symbol": pair.replace("USDT", ""),
                "price": float(ticker.get("lastPrice", 0)),
                "change": float(ticker.get("priceChangePercent", 0)),
                "volume": float(ticker.get("quoteVolume", 0))
            })

        # Indice de peur/avidité via alternative.me
        fear_greed = requests.get(
            "https://api.alternative.me/fng/?limit=1",
            timeout=5
        ).json()
        fg_value = fear_greed.get("data", [{}])[0].get("value", "N/A")
        fg_class = fear_greed.get("data", [{}])[0].get("value_classification", "N/A")

        return {
            "tokens": market_data,
            "fear_greed": {"value": fg_value, "classification": fg_class}
        }
    except Exception as e:
        return {"error": str(e)}


def analyze_market_movement(user_question: str, user_lang: str = "fr") -> str:
    """
    Analyse le mouvement du marché et explique pourquoi
    user_lang : langue détectée de l'utilisateur
    """
    market_data = get_market_overview()

    if "error" in market_data:
        return "❌ Impossible de récupérer les données de marché. Réessaie dans quelques instants."

    # Préparer le contexte pour Claude
    tokens_info = "\n".join([
        f"- {t['symbol']}: ${t['price']:,.2f} ({'+' if t['change'] >= 0 else ''}{t['change']:.2f}%) | Volume: ${t['volume']:,.0f}"
        for t in market_data["tokens"]
    ])

    fg = market_data["fear_greed"]
    fear_greed_info = f"Fear & Greed Index: {fg['value']}/100 ({fg['classification']})"

    prompt = f"""Tu es un expert crypto analyste. Voici les données de marché actuelles :

{tokens_info}

{fear_greed_info}

Question de l'utilisateur : "{user_question}"

Réponds en {user_lang}. Explique en 3-4 paragraphes :
1. Ce qui se passe sur le marché en ce moment
2. Les raisons probables (macro, news, sentiment, on-chain)
3. Ce que ça signifie pour l'utilisateur

Sois clair, pédagogique et concis. Termine toujours par un rappel DYOR.
N'utilise PAS de conseils d'achat/vente directs."""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    analysis = response.content[0].text

    # Header avec les données brutes
    header_lines = [
        "📊 **Aperçu du marché**",
        "━━━━━━━━━━━━━━━━━━",
    ]

    for t in market_data["tokens"]:
        emoji = "🟢" if t["change"] >= 0 else "🔴"
        sign = "+" if t["change"] >= 0 else ""
        header_lines.append(f"{emoji} {t['symbol']}: ${t['price']:,.2f} ({sign}{t['change']:.2f}%)")

    fg_emoji = "😱" if int(fg["value"]) < 30 else "😐" if int(fg["value"]) < 60 else "🤑"
    header_lines.append(f"{fg_emoji} Fear & Greed: {fg['value']}/100 — {fg['classification']}")
    header_lines.append("")
    header_lines.append("🧠 **Analyse IA**")
    header_lines.append("━━━━━━━━━━━━━━━━━━")
    header_lines.append(analysis)

    return "\n".join(header_lines)
