"""
Skill : Rug Pull Detector
Score de risque sur un token ou contrat via GoPlus (sans clé API)
"""

import requests
import os
import anthropic
from dotenv import load_dotenv

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

# Chain IDs supportés
CHAIN_IDS = {
    "eth": "1",
    "ethereum": "1",
    "bsc": "56",
    "bnb": "56",
    "binance": "56",
    "polygon": "137",
    "matic": "137",
    "arbitrum": "42161",
    "solana": "solana",
}

def detect_rug_pull(contract_address: str, chain: str = "bsc") -> str:
    """
    Analyse un contrat pour détecter les signes de rug pull
    GoPlus ne nécessite pas de clé API pour les requêtes basiques
    """
    chain_id = CHAIN_IDS.get(chain.lower(), "56")  # BSC par défaut

    risk_factors = []
    score = 0  # 0 = sûr, 100 = très dangereux

    try:
        # GoPlus Token Security API (gratuit sans clé)
        url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}"
        response = requests.get(
            url,
            params={"contract_addresses": contract_address},
            timeout=10
        ).json()

        result = response.get("result", {}).get(contract_address.lower(), {})

        if not result:
            return f"❌ Contrat `{contract_address}` introuvable sur la chaîne {chain.upper()}."

        # Analyse des facteurs de risque
        checks = {
            "is_honeypot": ("🍯 HONEYPOT détecté — Impossible de vendre !", 100),
            "is_blacklisted": ("⛔ Adresse blacklistée", 80),
            "is_proxy": ("🔄 Contrat proxy (peut changer)", 30),
            "is_mintable": ("🖨️ Token mintable à l'infini", 40),
            "can_take_back_ownership": ("👑 Owner peut reprendre contrôle", 50),
            "owner_change_balance": ("💸 Owner peut modifier les balances", 70),
            "hidden_owner": ("👻 Owner caché", 60),
            "selfdestruct": ("💣 Fonction selfdestruct présente", 50),
            "external_call": ("📞 Appels externes non vérifiés", 20),
            "is_anti_whale": ("🐋 Anti-whale activé", 10),
        }

        for key, (message, risk) in checks.items():
            if result.get(key) == "1":
                risk_factors.append(message)
                score = min(100, score + risk)

        # Infos générales
        buy_tax = result.get("buy_tax", "?")
        sell_tax = result.get("sell_tax", "?")
        holder_count = result.get("holder_count", "?")
        lp_locked = result.get("lp_locked", "0")

        if float(buy_tax or 0) > 10:
            risk_factors.append(f"💸 Taxe achat élevée : {buy_tax}%")
            score += 20
        if float(sell_tax or 0) > 10:
            risk_factors.append(f"💸 Taxe vente élevée : {sell_tax}%")
            score += 20
        if lp_locked == "0":
            risk_factors.append("🔓 Liquidité non verrouillée")
            score += 30

        score = min(score, 100)

        # Verdict
        if score == 0:
            verdict = "✅ FAIBLE RISQUE"
            verdict_color = "🟢"
        elif score < 30:
            verdict = "🟡 RISQUE MODÉRÉ — À surveiller"
            verdict_color = "🟡"
        elif score < 60:
            verdict = "🔴 RISQUE ÉLEVÉ — Très prudent"
            verdict_color = "🔴"
        else:
            verdict = "💀 DANGER EXTRÊME — Probable rug pull"
            verdict_color = "💀"

        lines = [
            f"🛡️ **Rug Pull Detector**",
            f"━━━━━━━━━━━━━━━━━━",
            f"📋 Contrat : `{contract_address[:10]}...{contract_address[-6:]}`",
            f"⛓️ Chaîne : {chain.upper()}",
            f"",
            f"**Score de risque : {score}/100**",
            f"{verdict_color} **{verdict}**",
            f"",
            f"📊 **Données**",
            f"• Taxe achat : {buy_tax}%",
            f"• Taxe vente : {sell_tax}%",
            f"• Nombre de holders : {holder_count}",
            f"• Liquidité verrouillée : {'✅ Oui' if lp_locked == '1' else '❌ Non'}",
        ]

        if risk_factors:
            lines.append("")
            lines.append("⚠️ **Facteurs de risque détectés :**")
            for rf in risk_factors:
                lines.append(f"• {rf}")

        lines.append("")
        lines.append("⚠️ _DYOR — Cette analyse ne remplace pas un audit complet._")

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Erreur lors de l'analyse : {str(e)}\nVérifie l'adresse du contrat."
