# Quick Start Guide

## Installation

### 1. Clone and Setup

```bash
git clone https://github.com/Rishi-Py/Stock-Screener-Agent.git
cd Stock-Screener-Agent
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
FINNHUB_API_KEY=your-finnhub-key  # Optional
```

## Usage Options

### Option 1: Command Line (Quickest)

Screen specific stocks:
```bash
python -m src.cli AAPL MSFT GOOGL
```

### Option 2: REST API

Start the server:
```bash
python -m src.api
```

Test it:
```bash
curl -X POST http://localhost:5000/api/screen \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT", "GOOGL"]}'
```

### Option 3: Python Script

Create a file `my_screen.py`:
```python
import asyncio
from src.agents.coordinator import MultiAgentCoordinator

async def main():
    coordinator = MultiAgentCoordinator()
    results = await coordinator.screen_stocks(["AAPL", "MSFT"])
    print(f"Top pick: {results['top_picks'][0]['symbol']}")

asyncio.run(main())
```

Run it:
```bash
python my_screen.py
```

### Option 4: n8n Workflow Automation

1. Install n8n:
```bash
npm install n8n -g
n8n start
```

2. Import workflows:
   - Open http://localhost:5678
   - Import `src/workflows/stock_screener_workflow.json`
   - Configure webhook URL to point to your API server
   - Activate the workflow

3. Trigger via webhook:
```bash
curl -X POST http://localhost:5678/webhook/stock-screener \
  -H "Content-Type: application/json" \
  -d '{"symbols": ["AAPL", "MSFT"]}'
```

## Key Features

### Multi-Agent System
- **Data Fetcher**: Gets fundamental data
- **Analysis Agent**: AI-powered GPT-4 analysis
- **Ranking Agent**: Scores stocks 0-100
- **Coordinator**: Orchestrates the workflow

### Scoring (100 points total)
- **30 points**: Growth (revenue + earnings)
- **25 points**: Valuation (P/E, PEG ratios)
- **20 points**: Financial Health (margins, ROE, FCF)
- **25 points**: AI Analysis (GPT-4 recommendation)

### Screening Criteria (Configurable)
- Minimum market cap: $1B
- Maximum P/E ratio: 30
- Minimum revenue growth: 15%
- Minimum earnings growth: 10%

## Common Use Cases

### Screen Growth Tech Stocks
```bash
python -m src.cli NVDA AMD PLTR SNOW CRWD --min-market-cap 5 --max-pe 40
```

### Daily Automated Screening
Use the `scheduled_screening.json` workflow in n8n to:
- Run daily at market open
- Screen a universe of stocks
- Email results
- Save to Google Sheets

### Custom Analysis
```python
config = {
    "min_market_cap": 10_000_000_000,  # $10B
    "max_pe_ratio": 20,
    "min_revenue_growth": 0.25,  # 25%
}
coordinator = MultiAgentCoordinator(config)
```

## Troubleshooting

### "No module named src"
Make sure you're in the project root directory.

### "OpenAI API key not found"
Check your `.env` file has `OPENAI_API_KEY` set.

### Tests failing
Install dependencies: `pip install -r requirements.txt`

### Rate limits
Reduce batch size or add delays between requests.

## Next Steps

- Check `docs/API.md` for API reference
- See `docs/ARCHITECTURE.md` for system design
- Try `examples/basic_screening.py` and `examples/custom_config.py`
- Read the full README for advanced features

## Support

For issues or questions, please open an issue on GitHub.
