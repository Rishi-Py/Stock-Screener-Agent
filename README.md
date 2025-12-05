# Stock Screener Agent 🚀

AI-powered growth stock screener agent with n8n + OpenAI + fundamentals data, featuring a multi-agent system architecture.

## Overview

Stock Screener Agent is an intelligent, multi-agent system designed to identify undervalued growth stocks by analyzing fundamental data through AI-powered analysis. The system uses OpenAI's GPT models to evaluate stocks and ranks them based on a comprehensive scoring methodology.

## Features

✨ **Multi-Agent Architecture**
- **Data Fetcher Agent**: Retrieves fundamental stock data from multiple sources (yfinance, Finnhub)
- **Analysis Agent**: AI-powered analysis using OpenAI GPT models
- **Ranking Agent**: Sophisticated scoring algorithm combining fundamentals and AI insights
- **Multi-Agent Coordinator**: Orchestrates the entire workflow with parallel processing support

🔄 **n8n Workflow Integration**
- Pre-built n8n workflows for automation
- Webhook-based stock screening
- Scheduled daily screening with email notifications
- Google Sheets integration for result tracking

📊 **Comprehensive Analysis**
- Revenue and earnings growth analysis
- Valuation metrics (P/E, PEG, Price-to-Book)
- Financial health indicators (ROE, debt-to-equity, cash flow)
- AI-powered investment thesis generation

🎯 **Flexible Screening Criteria**
- Configurable minimum market cap
- Maximum P/E ratio filtering
- Minimum growth rate requirements
- Customizable scoring weights

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key
- (Optional) Finnhub API key for enhanced data
- (Optional) n8n instance for workflow automation

### Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables: `cp .env.example .env`
4. Edit .env with your API keys

## Usage

### Command Line Interface

```bash
python -m src.cli AAPL MSFT GOOGL NVDA AMD
```

### REST API Server

```bash
python -m src.api
```

The server starts on `http://localhost:5000`.

## Documentation

See the full documentation in the `docs/` directory for:
- Complete setup instructions
- API reference
- n8n workflow configuration
- Scoring methodology details

## Disclaimer

This tool is for educational and informational purposes only. It does not constitute financial advice.
