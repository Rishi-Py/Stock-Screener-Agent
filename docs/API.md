# API Reference

## REST API Endpoints

### Health Check

**GET** `/health`

Check if the API server is running.

**Response:**
```json
{
  "status": "healthy",
  "service": "stock-screener-agent"
}
```

---

### Screen Stocks

**POST** `/api/screen`

Screen a custom list of stock symbols.

**Request Body:**
```json
{
  "symbols": ["AAPL", "MSFT", "GOOGL"],
  "batch_size": 5
}
```

**Parameters:**
- `symbols` (array, required): List of stock ticker symbols
- `batch_size` (integer, optional): Number of stocks to process in parallel (default: 5)

**Response:**
```json
{
  "workflow": "parallel_complete",
  "total_symbols": 3,
  "batch_size": 5,
  "stocks_ranked": 3,
  "qualified_stocks": 2,
  "top_picks": [
    {
      "symbol": "NVDA",
      "company_name": "NVIDIA Corporation",
      "score": 87.5,
      "breakdown": {
        "growth": 28,
        "valuation": 22,
        "financial_health": 18,
        "ai_analysis": 25
      },
      "fundamentals": {
        "market_cap": 2000000000000,
        "current_price": 450.0,
        "pe_ratio": 45.2,
        "revenue_growth": 1.265
      },
      "ai_recommendation": "Strong Buy",
      "passes_screening": true
    }
  ],
  "all_rankings": [...]
}
```

---

### Quick Screen

**POST** `/api/screen/quick`

Screen a pre-defined universe of stocks.

**Request Body:**
```json
{
  "universe": "tech"
}
```

**Parameters:**
- `universe` (string, optional): Stock universe to screen
  - `"tech"`: Major tech stocks
  - `"growth"`: High-growth stocks
  - `"all"`: Combined universe

**Response:**
Same structure as `/api/screen` endpoint.

---

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "error": "Missing required field 'symbols'"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error"
}
```

---

## Rate Limiting

The API currently does not enforce rate limiting, but be mindful of:
- OpenAI API rate limits
- Yahoo Finance data fetching limits
- Finnhub API rate limits (if configured)

## Authentication

Currently, no authentication is required. For production deployments, consider implementing:
- API key authentication
- JWT tokens
- OAuth2
