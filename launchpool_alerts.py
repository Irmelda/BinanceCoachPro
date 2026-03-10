"""
Skill : Token Analysis
Analyse complète d'un token via Binance API + CoinMarketCap
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv()
CMC_API_KEY = os.getenv("CMC_API_KEY")

def get_binance_price(symbol: str) -> dict:
    """Récupère le prix et les données de marché depuis Binance (public)"""
    symbol = symbol.upper()
    pair = f"{symbol}USDT"
    
    try:
        # Prix actuel
        ticker = requests.get(
            f"https://api.binance.com/api/v3/ticker/24hr?symbol={pair}",
            timeout=5
        ).json()

        return {
            "price": float(ticker.get("lastPrice", 0)),
            "change_24h": float(ticker.get("priceChangePercent", 0)),
            "volume_24h": float(ticker.get("quoteVolume", 0)),
            "high_24h": float(ticker.get("highPrice", 0)),
            "low_24h": float(ticker.get("lowPrice", 0)),
            "source": "Binance"
        }
    except Exception:
        return {}


def get_cmc_data(symbol: str) -> dict:
    """Récupère les métadonnées depuis CoinMarketCap"""
    headers = {"X-CMC_PRO_API_KEY": CMC_API_KEY}
    
    try:
        # Données de marché
        quote_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest"
        response = requests.get(
            quote_url,
            headers=headers,
            params={"symbol": symbol.upper(), "convert": "USD"},
            timeout=5
        ).json()

        data = response.get("data", {}).get(symbol.upper(), {})
        quote = data.get("quote", {}).get("USD", {})

        # Métadonnées (description, liens)
        meta_url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/info"
        meta = requests.get(
            meta_url,
            headers=headers,
            params={"symbol": symbol.upper()},
            timeout=5
        ).json()

        meta_data = meta.get("data", {}).get(symbol.upper(), {})

        return {
            "name": data.get("name", symbol),
            "symbol": symbol.upper(),
            "market_cap": quote.get("market_cap", 0),
            "rank": data.get("cmc_rank", "N/A"),
            "circulating_supply": data.get("circulating_supply", 0),
            "total_supply": data.get("total_supply", 0),
            "description": meta_data.get("description", "")[:300],
            "website": meta_data.get("urls", {}).get("website", [""])[0],
            "source": "CoinMarketCap"
        }
    except Exception:
        return {}


def analyze_token(symbol: str) -> str:
    """Analyse complète d'un token et retourne un message formaté"""
    symbol = symbol.upper().replace("$", "")

    binance_data = get_binance_price(symbol)
    cmc_data = get_cmc_data(symbol)

    if not binance_data and not cmc_data:
        return f"❌ Token **{symbol}** introuvable. Vérifie le symbole (ex: BTC, ETH, BNB)"

    price = binance_data.get("price") or 0
    change = binance_data.get("change_24h") or 0
    volume = binance_data.get("volume_24h") or 0
    high = binance_data.get("high_24h") or 0
    low = binance_data.get("low_24h") or 0
    market_cap = cmc_data.get("market_cap") or 0
    rank = cmc_data.get("rank", "N/A")
    name = cmc_data.get("name", symbol)

    change_emoji = "🟢" if change >= 0 else "🔴"
    change_sign = "+" if change >= 0 else ""

    lines = [
        f"🪙 **{name} ({symbol})**",
        f"━━━━━━━━━━━━━━━━━━",
        f"💵 Prix : **${price:,.4f}**",
        f"{change_emoji} Variation 24h : **{change_sign}{change:.2f}%**",
        f"📈 Haut 24h : ${high:,.4f}",
        f"📉 Bas 24h : ${low:,.4f}",
        f"💹 Volume 24h : ${volume:,.0f}",
        f"",
        f"📊 **Données de marché**",
        f"🏆 Rang CMC : #{rank}",
        f"💰 Market Cap : ${market_cap:,.0f}",
    ]

    if cmc_data.get("description"):
        lines.append("")
        lines.append(f"📝 **À propos :** _{cmc_data['description']}_")

    if cmc_data.get("website"):
        lines.append(f"🌐 Site : {cmc_data['website']}")

    lines.append("")
    lines.append("⚠️ _DYOR — Pas un conseil financier._")

    return "\n".join(lines)
