---
name: polymarket-nordic-trader
description: Trades Polymarket prediction markets focused on Scandinavian and Nordic events — Swedish politics, Norwegian economy, Danish infrastructure, Nordic business milestones (Spotify, Northvolt, Klarna), local weather extremes, and regional sports outcomes. Use when you want to capture alpha on underserved Nordic markets where local knowledge is a structural edge.
metadata:
  author: Diagnostikon
  version: '1.0'
  displayName: Nordic & Scandinavian Trader
  difficulty: beginner
---

# Nordic & Scandinavian Trader

> **This is a template.**  
> The default signal is keyword discovery + Swedish/Nordic news feed monitoring — remix it with Riksdagen API for legislative tracking, SCB (Statistics Sweden) data releases, Affärsvärlden market feeds, or Spotify investor relations signals.  
> The skill handles all the plumbing (market discovery, trade execution, safeguards). Your agent provides the alpha.

## Strategy Overview

Nordic markets are one of the most underserved categories on global prediction platforms. Traders with genuine local knowledge — Swedish politics, Scandinavian business news, Nordic weather patterns — hold structural information advantages over global retail traders.

This skill trades:
- **Swedish politics** — Government formation, Riksdag legislative milestones
- **Nordic business** — Spotify profitability, Northvolt recovery, Klarna/unicorn IPOs
- **Infrastructure** — Förbifart Stockholm, Malmö Arena, high-speed rail announcements
- **Sports** — Champions League Nordic teams, Swedish/Norwegian international competitions
- **Local weather** — Stockholm heatwaves, Öresund ice crossing, Oslo snowfall records
- **Culture** — Melodifestivalen viewership, Way Out West attendance

Key edge: the vast majority of Polymarket liquidity is US/global retail. Nordic-specific markets will have mispriced odds whenever the resolver requires local knowledge.

## Signal Logic

### Default Signal: Nordic News Feed + Market Mismatch

1. Discover markets mentioning Nordic/Scandinavian keywords
2. Monitor Swedish/Nordic RSS feeds: SVT, Aftonbladet, Di.se, Affärsvärlden
3. Check local weather data from SMHI (Swedish Meteorological Institute) for weather markets
4. Compare current news consensus with market price
5. Enter when the global market clearly hasn't incorporated locally-obvious information

### Remix Ideas

- **SMHI API**: https://www.smhi.se/klimatdata — Official Swedish weather data
- **Riksdagen API**: https://data.riksdagen.se/ — Parliamentary voting and legislation tracking
- **SCB (Statistics Sweden)**: https://www.scb.se/en/ — Economic data releases
- **Avanza/Nordnet**: Swedish stock sentiment as proxy for Spotify/Nordic tech markets
- **Allsvenskan data**: Football results and standings for sports markets

## Market Categories Tracked

```python
NORDIC_KEYWORDS = [
    "Sweden", "Sverige", "Stockholm", "Malmö", "Göteborg",
    "Norway", "Norge", "Oslo", "Denmark", "Danmark", "Copenhagen",
    "Spotify", "Northvolt", "Klarna", "Ericsson", "Volvo",
    "Riksdag", "government", "election", "Nordic", "Scandinavian",
    "IKEA", "H&M", "Skanska", "Atlas Copco",
    "Melodifestivalen", "ABBA", "Way Out West",
    "Champions League", "Swedish football", "Zlatan",
    "SMHI", "Öresund", "Arctic", "fjord"
]
```

## Risk Parameters

| Parameter | Default | Notes |
|-----------|---------|-------|
| Max position size | $20 USDC | Nordic markets may be illiquid |
| Min market volume | $1,000 | Accept lower liquidity for edge opportunity |
| Max bid-ask spread | 20% | Niche markets have wider spreads |
| Min days to resolution | 3 | Local events can resolve quickly |
| Max open positions | 8 | Diversify across Nordic themes |

## Local Knowledge Edge

### Information Advantage Examples
- **Förbifart Stockholm**: A Swedish civil engineer knows the tunnel's actual completion status better than US retail traders
- **Northvolt bankruptcy**: Swedish business press covered the restructuring in detail months before English-language coverage
- **SMHI winter forecasts**: Local seasonal weather outlooks are published in Swedish first
- **Melodifestivalen**: SVT viewership trends visible to Swedish residents immediately

### Timing Edge
Swedish/Nordic news typically breaks in CET timezone (UTC+1/+2). US-dominated Polymarket markets take 2–6 hours to reprice on Nordic news.

## Key Data Sources

- **SMHI** (Weather): https://www.smhi.se/
- **Riksdagen** (Parliament): https://data.riksdagen.se/
- **SCB** (Statistics): https://www.scb.se/
- **SVT Nyheter**: https://www.svt.se/nyheter/
- **Di.se** (Business): https://www.di.se/

## Installation & Setup

```bash
clawhub install polymarket-nordic-trader
```

Requires: `SIMMER_API_KEY` environment variable.

## Cron Schedule

Runs every 15 minutes (`*/15 * * * *`). Nordic events follow business hours (CET); tighter polling during 06:00–22:00 CET recommended in remixes.

## Safety & Execution Mode

**The skill defaults to paper trading (`venue="sim"`). Real trades only execute when `--live` is passed explicitly.**

| Scenario | Mode | Financial risk |
|----------|------|----------------|
| `python trader.py` | Paper (sim) | None |
| Cron / automaton | Paper (sim) | None |
| `python trader.py --live` | Live (polymarket) | Real USDC |

The automaton cron is set to `null` — it does not run on a schedule until you configure it in the Simmer UI. `autostart: false` means it won't start automatically on install.

## Required Credentials

| Variable | Required | Notes |
|----------|----------|-------|
| `SIMMER_API_KEY` | Yes | Trading authority — keep this credential private. Do not place a live-capable key in any environment where automated code could call `--live`. |

## Tunables (Risk Parameters)

All risk parameters are declared in `clawhub.json` as `tunables` and adjustable from the Simmer UI without code changes. They use `SIMMER_`-prefixed env vars so `apply_skill_config()` can load them securely.

| Variable | Default | Purpose |
|----------|---------|---------|
| `SIMMER_NORDIC_MAX_POSITION` | `20` | Max USDC per trade |
| `SIMMER_NORDIC_MIN_VOLUME` | `1000` | Min market volume filter (USD) |
| `SIMMER_NORDIC_MAX_SPREAD` | `0.20` | Max bid-ask spread (0.10 = 10%) |
| `SIMMER_NORDIC_MIN_DAYS` | `3` | Min days until market resolves |
| `SIMMER_NORDIC_MAX_POSITIONS` | `8` | Max concurrent open positions |

## Dependency

`simmer-sdk` is published on PyPI by Simmer Markets.
- PyPI: https://pypi.org/project/simmer-sdk/
- GitHub: https://github.com/SpartanLabsXyz/simmer-sdk
- Publisher: hello@simmer.markets

Review the source before providing live credentials if you require full auditability.
