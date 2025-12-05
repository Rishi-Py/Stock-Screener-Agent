"""
Data Fetcher Agent - Retrieves fundamental data for stocks.
"""

import os
from typing import Any, Dict, List, Optional
import yfinance as yf
import finnhub
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_agent import BaseAgent


class DataFetcherAgent(BaseAgent):
    """Agent responsible for fetching fundamental stock data."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Data Fetcher Agent."""
        super().__init__("DataFetcher", config)
        self.finnhub_client = None
        
        # Initialize Finnhub client if API key is available
        api_key = os.getenv("FINNHUB_API_KEY")
        if api_key:
            self.finnhub_client = finnhub.Client(api_key=api_key)
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch fundamental data for given stock symbols.
        
        Args:
            input_data: Dictionary with 'symbols' key containing list of stock symbols
            
        Returns:
            Dictionary with stock data
        """
        self.validate_input(input_data, ["symbols"])
        symbols = input_data["symbols"]
        
        self.log_execution(f"Fetching data for {len(symbols)} symbols")
        
        results = {}
        for symbol in symbols:
            try:
                data = await self._fetch_stock_data(symbol)
                results[symbol] = data
                self.log_execution(f"Successfully fetched data for {symbol}")
            except Exception as e:
                self.log_execution(f"Error fetching data for {symbol}: {str(e)}", "error")
                results[symbol] = {"error": str(e)}
        
        return {
            "agent": self.name,
            "symbols_processed": len(symbols),
            "data": results
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _fetch_stock_data(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch comprehensive stock data for a single symbol.
        
        Args:
            symbol: Stock ticker symbol
            
        Returns:
            Dictionary containing fundamental data
        """
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Extract key fundamental metrics
        data = {
            "symbol": symbol,
            "company_name": info.get("longName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", 0),
            "current_price": info.get("currentPrice", 0),
            "pe_ratio": info.get("trailingPE", None),
            "forward_pe": info.get("forwardPE", None),
            "peg_ratio": info.get("pegRatio", None),
            "price_to_book": info.get("priceToBook", None),
            "revenue": info.get("totalRevenue", 0),
            "revenue_growth": info.get("revenueGrowth", None),
            "earnings_growth": info.get("earningsGrowth", None),
            "profit_margins": info.get("profitMargins", None),
            "operating_margins": info.get("operatingMargins", None),
            "roe": info.get("returnOnEquity", None),
            "debt_to_equity": info.get("debtToEquity", None),
            "free_cash_flow": info.get("freeCashflow", 0),
            "operating_cash_flow": info.get("operatingCashflow", 0),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh", 0),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow", 0),
            "analyst_recommendation": info.get("recommendationKey", "N/A"),
            "target_price": info.get("targetMeanPrice", None),
        }
        
        # Add Finnhub data if available
        if self.finnhub_client:
            try:
                finnhub_metrics = self.finnhub_client.company_basic_financials(symbol, 'all')
                data["finnhub_metrics"] = finnhub_metrics
            except Exception as e:
                self.log_execution(f"Could not fetch Finnhub data for {symbol}: {str(e)}", "warning")
        
        return data
