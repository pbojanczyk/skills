---
name: polymarket-esports-trader
description: Trades esports tournament, game release, and streaming milestone prediction markets on Polymarket using live match data and viewership signals.
metadata:
  author: Diagnostikon
  version: "1.0"
  displayName: Esports & Gaming Trader
  difficulty: intermediate
---

# Esports & Gaming Trader

> **This is a template.**
> The default signal is keyword-based market discovery combined with probability-extreme detection — remix it with the data sources listed in the Edge Thesis below.
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Elo-model win probability vs Polymarket price divergence. Twitch viewership momentum as leading indicator.

## Edge Thesis

Esports bracket markets systematically overestimate crowd-favorite teams by 8–18% vs Elo-based models (documented in prediction market research, 2023–2025). Game release date markets are highly accurate 6 months out but get noisy 30 days before — that's when the spread widens and the signal appears. Liquipedia has real-time bracket and match data you can diff against market prices.

### Remix Signal Ideas
- **Liquipedia API**: https://liquipedia.net/commons/Liquipedia:API_documentation — Match results, brackets, team stats for 30+ esports titles
- **Steam Charts**: https://store.steampowered.com/api/ — Concurrent player peaks as launch signal
- **TwitchTracker**: https://twitchtracker.com/api — Viewership momentum — 24h spike often precedes market move

## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only with `--live` flag.**

| Scenario | Mode | Financial risk |
|---|---|---|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

`autostart: false` and `cron: null` — nothing runs automatically until you configure it in Simmer UI.

## Required Credentials

| Variable | Required | Notes |
|---|---|---|
| `SIMMER_API_KEY` | Yes | Trading authority. Treat as high-value credential. |

## Tunables (Risk Parameters)

All declared as `tunables` in `clawhub.json` and adjustable from the Simmer UI.

| Variable | Default | Purpose |
|---|---|---|
| `SIMMER_MAX_POSITION` | See clawhub.json | Max USDC per trade |
| `SIMMER_MIN_VOLUME` | See clawhub.json | Min market volume filter |
| `SIMMER_MAX_SPREAD` | See clawhub.json | Max bid-ask spread |
| `SIMMER_MIN_DAYS` | See clawhub.json | Min days until resolution |
| `SIMMER_MAX_POSITIONS` | See clawhub.json | Max concurrent open positions |

## Dependency

`simmer-sdk` by Simmer Markets (SpartanLabsXyz)
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
