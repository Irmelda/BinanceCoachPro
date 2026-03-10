"""
Skill : Binance Link Check
Vérifie si un lien est officiel Binance ou du phishing
"""

import requests

# Domaines officiels Binance
OFFICIAL_BINANCE_DOMAINS = [
    "binance.com",
    "binance.org",
    "binance.us",
    "binance.je",
    "binance.cc",
    "binancecoin.org",
    "bnbchain.org",
    "academy.binance.com",
    "research.binance.com",
    "coinmarketcap.com",  # Owned by Binance
    "trust.app",
    "trustwallet.com",
]

PHISHING_KEYWORDS = [
    "binance-", "-binance", "binance_", "_binance",
    "bìnance", "bínance", "bïnance", "binànce",
    "airdrop", "free-bnb", "claim-bnb", "bonus-bnb",
]

def check_link(url: str) -> dict:
    """
    Vérifie si un lien est officiel ou suspect.
    Retourne un dict avec le résultat et le score de risque.
    """
    url = url.lower().strip()
    
    # Supprimer le protocole pour analyse
    clean_url = url.replace("https://", "").replace("http://", "").replace("www.", "")
    domain = clean_url.split("/")[0]

    result = {
        "url": url,
        "domain": domain,
        "is_official": False,
        "risk_score": 0,  # 0 = sûr, 100 = très dangereux
        "warnings": [],
        "verdict": ""
    }

    # Vérification domaine officiel
    for official in OFFICIAL_BINANCE_DOMAINS:
        if domain == official or domain.endswith("." + official):
            result["is_official"] = True
            result["risk_score"] = 0
            result["verdict"] = "✅ OFFICIEL"
            return result

    # Vérification phishing keywords
    for keyword in PHISHING_KEYWORDS:
        if keyword in domain:
            result["risk_score"] += 40
            result["warnings"].append(f"Domaine suspect contenant '{keyword}'")

    # HTTP non sécurisé
    if url.startswith("http://"):
        result["risk_score"] += 20
        result["warnings"].append("Connexion non sécurisée (HTTP)")

    # Vérification GoPlus (Phishing Site Detection) - sans clé API
    try:
        goplus_url = f"https://api.gopluslabs.io/api/v1/phishing_site?url={url}"
        response = requests.get(goplus_url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("result", {}).get("is_phishing_site") == "1":
                result["risk_score"] = 100
                result["warnings"].append("⚠️ Détecté comme site de PHISHING par GoPlus")
    except Exception:
        pass  # GoPlus indisponible, on continue sans

    # Verdict final
    if result["risk_score"] == 0:
        result["verdict"] = "⚠️ INCONNU — Non officiel Binance"
    elif result["risk_score"] < 40:
        result["verdict"] = "🟡 SUSPECT — Prudence recommandée"
    elif result["risk_score"] < 70:
        result["verdict"] = "🔴 DANGEREUX — Ne pas cliquer"
    else:
        result["verdict"] = "💀 PHISHING CONFIRMÉ — Ne pas cliquer !"

    return result


def format_response(result: dict) -> str:
    """Formate le résultat pour l'affichage Telegram"""
    lines = [
        f"🔗 **Analyse du lien**",
        f"━━━━━━━━━━━━━━━━━━",
        f"🌐 Domaine : `{result['domain']}`",
        f"📊 Score de risque : {result['risk_score']}/100",
        f"",
        f"**Verdict : {result['verdict']}**",
    ]

    if result["warnings"]:
        lines.append("")
        lines.append("⚠️ **Alertes :**")
        for w in result["warnings"]:
            lines.append(f"• {w}")

    if result["is_official"]:
        lines.append("")
        lines.append("✅ Ce lien appartient au domaine officiel Binance.")
    else:
        lines.append("")
        lines.append("💡 _Toujours vérifier sur binance.com directement._")

    return "\n".join(lines)
