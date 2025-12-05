"""
Analysis Agent - AI-powered analysis using OpenAI.
"""

import os
from typing import Any, Dict, List, Optional
from openai import AsyncOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

from .base_agent import BaseAgent


class AnalysisAgent(BaseAgent):
    """Agent responsible for AI-powered stock analysis using OpenAI."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Analysis Agent."""
        super().__init__("AnalysisAgent", config)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze stock data using OpenAI.
        
        Args:
            input_data: Dictionary with 'stock_data' key containing fundamental data
            
        Returns:
            Dictionary with AI analysis results
        """
        self.validate_input(input_data, ["stock_data"])
        stock_data = input_data["stock_data"]
        
        self.log_execution(f"Analyzing {len(stock_data)} stocks")
        
        analyses = {}
        for symbol, data in stock_data.items():
            if "error" in data:
                analyses[symbol] = {"error": data["error"]}
                continue
            
            try:
                analysis = await self._analyze_stock(symbol, data)
                analyses[symbol] = analysis
                self.log_execution(f"Completed analysis for {symbol}")
            except Exception as e:
                self.log_execution(f"Error analyzing {symbol}: {str(e)}", "error")
                analyses[symbol] = {"error": str(e)}
        
        return {
            "agent": self.name,
            "stocks_analyzed": len(analyses),
            "analyses": analyses
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
    async def _analyze_stock(self, symbol: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single stock using OpenAI.
        
        Args:
            symbol: Stock ticker symbol
            data: Fundamental data for the stock
            
        Returns:
            Dictionary containing AI analysis
        """
        prompt = self._create_analysis_prompt(symbol, data)
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert financial analyst specializing in growth stock analysis. "
                        "Analyze stocks based on fundamental data and identify undervalued growth opportunities. "
                        "Provide structured, objective analysis focusing on growth metrics, valuation, "
                        "financial health, and overall investment potential."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3,
            max_tokens=1500
        )
        
        analysis_text = response.choices[0].message.content
        
        # Extract structured insights
        return {
            "symbol": symbol,
            "analysis": analysis_text,
            "model_used": self.model,
            "tokens_used": response.usage.total_tokens if response.usage else 0
        }
    
    def _create_analysis_prompt(self, symbol: str, data: Dict[str, Any]) -> str:
        """
        Create a detailed analysis prompt for OpenAI.
        
        Args:
            symbol: Stock ticker symbol
            data: Fundamental data
            
        Returns:
            Formatted prompt string
        """
        prompt = f"""
Analyze the following stock for undervalued growth potential:

**Company: {data.get('company_name', 'N/A')} ({symbol})**
**Sector:** {data.get('sector', 'N/A')}
**Industry:** {data.get('industry', 'N/A')}

**Valuation Metrics:**
- Market Cap: ${data.get('market_cap', 0):,.0f}
- Current Price: ${data.get('current_price', 0):.2f}
- P/E Ratio: {data.get('pe_ratio', 'N/A')}
- Forward P/E: {data.get('forward_pe', 'N/A')}
- PEG Ratio: {data.get('peg_ratio', 'N/A')}
- Price-to-Book: {data.get('price_to_book', 'N/A')}

**Growth Metrics:**
- Revenue Growth: {self._format_percentage(data.get('revenue_growth'))}
- Earnings Growth: {self._format_percentage(data.get('earnings_growth'))}
- Total Revenue: ${data.get('revenue', 0):,.0f}

**Profitability:**
- Profit Margin: {self._format_percentage(data.get('profit_margins'))}
- Operating Margin: {self._format_percentage(data.get('operating_margins'))}
- ROE: {self._format_percentage(data.get('roe'))}

**Financial Health:**
- Debt-to-Equity: {data.get('debt_to_equity', 'N/A')}
- Free Cash Flow: ${data.get('free_cash_flow', 0):,.0f}
- Operating Cash Flow: ${data.get('operating_cash_flow', 0):,.0f}

**Price Range:**
- 52-Week High: ${data.get('fifty_two_week_high', 0):.2f}
- 52-Week Low: ${data.get('fifty_two_week_low', 0):.2f}
- Analyst Target: ${data.get('target_price', 0):.2f}

Please provide:
1. **Growth Assessment**: Evaluate the company's growth trajectory and sustainability
2. **Valuation Analysis**: Is the stock undervalued relative to its growth potential?
3. **Risk Factors**: Key risks and concerns
4. **Investment Thesis**: Overall recommendation (Strong Buy, Buy, Hold, Sell, Strong Sell)
5. **Growth Score**: Rate from 1-10 based on undervalued growth potential

Keep the analysis concise and focused on actionable insights.
"""
        return prompt
    
    @staticmethod
    def _format_percentage(value: Optional[float]) -> str:
        """Format percentage values."""
        if value is None:
            return "N/A"
        return f"{value * 100:.2f}%"
