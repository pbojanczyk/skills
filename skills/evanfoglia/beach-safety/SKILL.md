---
name: beach-safety
version: 1.0.1
description: Comprehensive beach safety conditions for any beach in the world — rip current risk, waves, swell, wind, temperature, UV index, and safety scores. MCP server + CLI.
author: Evan Foglia
metadata:
  env:
    OPENUV_API_KEY:
      description: Optional OpenUV API key for UV data (free at openuv.io, 50/day)
      required: false
  bins:
    - python3
---

# Beach Safety MCP

Get comprehensive beach and surf conditions for any beach location worldwide — just say the beach name.

## Installation

```bash
# Install via clawhub
npx clawhub install beach-safety

# Or clone and configure manually
git clone https://github.com/evanfoglia/beach-safety-mcp
```

## Setup

1. Add to mcporter (`~/.openclaw/workspace/config/mcporter.json`):
```json
{
  "beach-safety": {
    "command": "python3",
    "args": ["/full/path/to/beach-safety-mcp/src/server.py"]
  }
}
```

2. Set OpenUV API key for UV data (free at openuv.io, 50/day):
```bash
export OPENUV_API_KEY="your-free-key"
```

## Usage

### From AI (via mcporter)
```
get_beach_report(beach_name="Waikiki")
get_beach_report(beach_name="Bondi Beach, Sydney")
get_beach_json(beach_name="Cocoa Beach, FL")
get_surf_forecast(lat=33.985, lon=-118.469)
```

### From CLI
```bash
python3 beach_lookup.py "Waikiki"
python3 beach_lookup.py "Bondi Beach, Sydney"
```

## Tools

### get_beach_report
Full text report with safety score, waves, swell, wind, temperature, UV, recommendations.

```
get_beach_report(beach_name="Venice Beach, CA")
```

### get_beach_json
Same data as JSON for programmatic use.

```
get_beach_json(beach_name="Huntington Beach, CA")
```

### get_surf_forecast
Surf-specific: wave height, swell, period, direction, rip risk.

```
get_surf_forecast(lat=33.985, lon=-118.469)
```

### get_uv_forecast
UV index with sun protection guidance.

```
get_uv_forecast(lat=33.985, lon=-118.469, openuv_api_key="key")
```

## Data Sources (all free)

| Source | Data |
|--------|------|
| OpenStreetMap / Photons | Beach name → coordinates |
| Open-Meteo Marine | Wave height, swell, ocean currents |
| Open-Meteo Weather | Air temp, wind, precipitation |
| NOAA NWS | Rip current risk, surf zone forecast |
| OpenUV | UV index (optional, 50/day free) |

## Safety Score

| Score | Meaning | Action |
|-------|---------|--------|
| 9-10 | Generally safe | Enjoy with normal precautions |
| 7-8 | Minor concerns | Caution advised |
| 4-6 | Caution | Swim near lifeguard |
| 1-3 | Dangerous | **Stay out of the water** |
