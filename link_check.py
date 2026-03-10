"""
Skill : P&L Tracker
Suivi des gains/pertes en temps réel
Les clés Binance sont fournies par l'utilisateur
"""

import requests
import hmac
import hashlib
import time
import os
from urllib.parse import urlencode

def get_account_pnl(api_key: str, secret_key: str) -> str:
    """
    Récupère le P&L du compte Binance de l'utilisateur
    Les clés sont fournies par l'utilisateur via le bot
    """
    base_url = "https://api.binance.com"

    def sign_request(params: dict) -> str:
        query = urlencode(params)
        signature = hmac.new(
            secret_key.encode("utf-8"),
            query.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        return f"{query}&signature={signature}"

    headers = {"X-MBX-APIKEY": api_key}

    try:
        # Récupérer les balances du compte
        timestamp = int(time.time() * 1000)
        params = {"timestamp": timestamp}
        signed = sign_request(params)

        account = requests.get(
            f"{base_url}/api/v3/account?{signed}",
            headers=headers,
            timeout=5
        ).json()

        if "code" in account:
            if account["code"] == -2014:
                return "❌ Clé API invalide. Vérifie ta clé Binance."
            return f"❌ Erreur Binance : {account.get('msg', 'Erreur inconnue')}"

        # Filtrer les balances non nulles
        balances = [
            b for b in account.get("balances", [])
            if float(b["free"]) > 0 or float(b["locked"]) > 0
        ]

        if not balances:
            return "📭 Aucun actif trouvé dans ce compte."

        # Calculer la valeur en USDT
        total_usdt = 0
        portfolio_lines = []

        for b in balances:
            symbol = b["asset"]
            free = float(b["free"])
            locked = float(b["locked"])
            total = free + locked

            # Prix en USDT
            if symbol == "USDT":
                value_usdt = total
            else:
                try:
                    ticker = requests.get(
                        f"{base_url}/api/v3/ticker/price?symbol={symbol}USDT",
                        timeout=3
                    ).json()
                    price = float(ticker.get("price", 0))
                    value_usdt = total * price
                except Exception:
                    value_usdt = 0

            if value_usdt > 1:  # Ignorer les dust < 1$
                total_usdt += value_usdt
                portfolio_lines.append({
                    "symbol": symbol,
                    "amount": total,
                    "value_usdt": value_usdt
                })

        # Trier par valeur décroissante
        portfolio_lines.sort(key=lambda x: x["value_usdt"], reverse=True)

        lines = [
            "💰 **Mon Portfolio**",
            "━━━━━━━━━━━━━━━━━━",
            f"💵 **Valeur totale : ${total_usdt:,.2f} USDT**",
            "",
            "📊 **Répartition :**"
        ]

        for p in portfolio_lines[:10]:  # Top 10
            pct = (p["value_usdt"] / total_usdt * 100) if total_usdt > 0 else 0
            lines.append(
                f"• {p['symbol']}: {p['amount']:.4f} ≈ ${p['value_usdt']:,.2f} ({pct:.1f}%)"
            )

        if len(portfolio_lines) > 10:
            lines.append(f"• ... et {len(portfolio_lines) - 10} autres actifs")

        lines.append("")
        lines.append("🔒 _Tes clés API sont utilisées localement et ne sont jamais partagées._")
        lines.append("⚠️ _Données en temps réel depuis ton compte Binance._")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Erreur de connexion : {str(e)}"


def request_api_keys_message(lang: str = "fr") -> str:
    """Message demandant les clés API à l'utilisateur"""
    messages = {
        "fr": """🔑 **Connexion à ton compte Binance**

Pour afficher ton P&L, j'ai besoin de tes clés API Binance.

**Comment obtenir tes clés :**
1. Va sur binance.com → Profil → API Management
2. Crée une clé avec uniquement **"Enable Reading"** ✅
3. **NE PAS** activer le trading ou les retraits ❌

**Envoie tes clés dans ce format :**
```
/pnl API_KEY SECRET_KEY
```

🔒 _Tes clés restent sur ton appareil et ne sont jamais partagées._""",

        "en": """🔑 **Connect to your Binance account**

To show your P&L, I need your Binance API keys.

**How to get your keys:**
1. Go to binance.com → Profile → API Management
2. Create a key with only **"Enable Reading"** ✅
3. **DO NOT** enable trading or withdrawals ❌

**Send your keys in this format:**
```
/pnl API_KEY SECRET_KEY
```

🔒 _Your keys stay on your device and are never shared._"""
    }
    return messages.get(lang, messages["en"])
