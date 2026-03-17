# 🚀 BinanceCoach Pro — Setup Guide

> An OpenClaw AI agent for the Binance ecosystem

---

## 📋 Prerequisites

- Windows, macOS, or Linux
- Node.js v22 or higher → [nodejs.org](https://nodejs.org)
- A Telegram account
- API keys (see below)

---

## 🔑 Required API Keys

| Service | Purpose | Link |
|---|---|---|
| Anthropic (Claude) | AI brain | [console.anthropic.com](https://console.anthropic.com) |
| CoinMarketCap | Token metadata | [coinmarketcap.com/api](https://coinmarketcap.com/api) |
| X (Twitter) | Binance news feed | [developer.twitter.com](https://developer.twitter.com) |
| Telegram Bot | Chat interface | [@BotFather](https://t.me/BotFather) |

> GoPlus Security API requires no key for basic usage ✅
> Binance Public API requires no key ✅

---

## ⚙️ Installation

### Step 1 — Install OpenClaw

**macOS / Linux:**
```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

**Windows (PowerShell as Admin):**
```powershell
iwr -useb https://openclaw.ai/install.ps1 -OutFile install.ps1; powershell -ExecutionPolicy Bypass -File install.ps1
```

### Step 2 — Run Onboarding
```bash
openclaw onboard
```

During onboarding:
- ✅ Select **QuickStart** mode
- ✅ Select **Anthropic** as model provider
- ✅ Paste your **Anthropic API key**
- ✅ Select **claude-sonnet-4-6** as default model
- ✅ Select **Telegram (Bot API)** as channel
- ✅ Paste your **Telegram Bot Token**
- ✅ Enable **session-memory** hook
- ✅ Select **Open Web UI** to launch dashboard

### Step 3 — Configure the Agent

Copy `AGENTS.md` and `IDENTITY.md` to your OpenClaw workspace:

```
~/.openclaw/workspace/AGENTS.md
~/.openclaw/workspace/IDENTITY.md
```

### Step 4 — Add API Keys

Open `~/.openclaw/openclaw.json` and add your keys in the `env` section:

```json
"env": {
  "CMC_API_KEY": "YOUR_COINMARKETCAP_KEY",
  "X_BEARER_TOKEN": "YOUR_X_BEARER_TOKEN"
}
```

### Step 5 — Launch the Gateway

```bash
openclaw gateway start
```

Or on Windows if needed:
```powershell
node "%APPDATA%\npm\node_modules\openclaw\dist\index.js" gateway --port 18789
```

### Step 6 — Approve Telegram Pairing

In Telegram, send `/start` to your bot. It will give you a pairing code.

Then approve it:
```bash
openclaw pairing approve telegram YOUR_PAIRING_CODE
```

---

## ✅ You're Live!

Open Telegram and send `/start` to your bot. You should see:

```
━━━━━━━━━━━━━━━━━━━━━
🤖 BinanceCoach Pro
Your elite crypto intelligence assistant
━━━━━━━━━━━━━━━━━━━━━
```

---

## 🤖 Features

| Feature | Command |
|---|---|
| 🔗 Phishing Link Check | Share any URL |
| 🪙 Token Analysis | "Analyze BTC" |
| 📊 Market Movement | "Why is market moving?" |
| 🐦 Binance News | "Latest Binance news" |
| 🛡️ Rug Pull Detector | Share contract address |
| 📅 Launchpool Alerts | "Launchpool opportunities" |
| 💰 P&L Tracker | "My P&L" |
| 🌍 Multi-language | Auto-detected |

---

## 🔒 Security Notes

- Never expose your gateway to the public internet
- Use strong tokens
- Keep your API keys private
- For production use, run inside Docker or a VM
