---
name: gprophet-api
description: AI-powered stock prediction and market analysis for global markets
homepage: https://www.gprophet.com
metadata:
  clawdbot:
    emoji: "📈"
    requires:
      env: ["GPROPHET_API_KEY"]
    primaryEnv: "GPROPHET_API_KEY"
---

# G-Prophet API Skills

AI-powered stock prediction and market analysis capabilities for OpenClaw agents.

## Features

- 📈 Stock price prediction (1-30 days, multiple AI algorithms)
- 🌍 Multi-market support (US, CN, HK, Crypto)
- 🤖 Multiple AI algorithms (G-Prophet2026V1, LSTM, Transformer, etc.)
- 📊 Technical analysis (RSI, MACD, Bollinger Bands, KDJ)
- 💹 Market sentiment analysis (Fear & Greed, market overview)
- 🔍 Deep multi-agent analysis (5-dimension evaluation)
- 📦 Batch quote (up to 20 symbols in one call)
- 🧠 AI stock analysis report (58 points, async)
- 🔔 Webhook callbacks for async analysis tasks
- 🐍 Official Python SDK with auto-retry and async polling
- 🔌 MCP Server for AI agent integration (13 tools)
- ⚡ Rate limiting & quota management
- 📊 Account balance & usage statistics endpoints

## Quick Start

Get up and running in 5 minutes:

1. Get API key at https://www.gprophet.com/settings/api-keys
2. Set environment variable: `export GPROPHET_API_KEY="gp_sk_..."`
3. Make your first prediction:

```bash
curl -X POST "https://www.gprophet.com/api/external/v1/predictions/predict" \
  -H "X-API-Key: $GPROPHET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"symbol": "AAPL", "market": "US", "days": 7}'
```

### Python SDK

```bash
pip install gprophet
```

```python
from gprophet import GProphet

client = GProphet(api_key="gp_sk_...")
result = client.predict("AAPL", market="US", days=7)
print(result["data"]["predicted_price"])
```

### MCP Server

```json
{
  "mcpServers": {
    "gprophet": {
      "command": "python",
      "args": ["path/to/gprophet_mcp_server.py"],
      "env": { "GPROPHET_API_KEY": "gp_sk_..." }
    }
  }
}
```

See [QUICK_START.md](./QUICK_START.md) for more examples.

## Security & Authentication

This skill requires a G-Prophet API key to access the external prediction service.

### Getting Your API Key

1. Visit https://www.gprophet.com/settings/api-keys
2. Create a new API key (format: `gp_sk_*`)
3. For testing, consider creating a limited-scope key with minimal permissions

### Secure Configuration

**Recommended**: Use environment variables to store your API key securely:

```bash
export GPROPHET_API_KEY="gp_sk_[REDACTED]_key_here"
```

⚠️ **Security Best Practices**:
- Never commit API keys to version control
- Use test/limited keys for evaluation
- Rotate keys regularly
- Monitor usage and billing at https://www.gprophet.com/dashboard
- Revoke keys immediately if compromised

## Rate Limiting & Quotas

- Default: 60 requests per minute per API Key
- Response headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
- Daily/monthly quotas configurable per key
- HTTP 429 returned when limits exceeded

## Points & Billing

All API calls consume points from your G-Prophet account:
- Stock prediction: 10-20 points (varies by market)
- Technical analysis / Market data: 5 points
- Batch quote: 5 × number of symbols
- AI stock analysis: 58 points
- Deep analysis: 150 points
- Account/info endpoints: Free

Monitor your usage at: https://www.gprophet.com/dashboard

## Privacy & Data

This skill sends stock symbols and market codes to the external G-Prophet API (https://www.gprophet.com). No personal data or trading credentials are transmitted. Review the privacy policy at https://www.gprophet.com/privacy

## Documentation

- **[SKILL.md](./SKILL.md)** - Complete API documentation and endpoint reference
- **[SECURITY.md](./SECURITY.md)** - Security best practices and credential management
- **[COST_MANAGEMENT.md](./COST_MANAGEMENT.md)** - Points pricing, budget planning, and cost optimization
- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[CHANGELOG.md](./CHANGELOG.md)** - Version history and release notes

## Support

- Documentation: https://www.gprophet.com/docs
- API Status: https://www.gprophet.com/status
- Support: support@gprophet.com

## License

MIT