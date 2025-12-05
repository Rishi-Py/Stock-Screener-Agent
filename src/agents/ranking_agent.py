"""
Ranking Agent - Ranks stocks based on analysis and fundamentals.
"""

from typing import Any, Dict, List, Optional, Tuple
import re

from .base_agent import BaseAgent


class RankingAgent(BaseAgent):
    """Agent responsible for ranking stocks by undervalued growth potential."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the Ranking Agent."""
        super().__init__("RankingAgent", config)
        
        # Default screening criteria
        self.min_market_cap = config.get("min_market_cap", 1_000_000_000) if config else 1_000_000_000
        self.max_pe_ratio = config.get("max_pe_ratio", 30) if config else 30
        self.min_revenue_growth = config.get("min_revenue_growth", 0.15) if config else 0.15
        self.min_earnings_growth = config.get("min_earnings_growth", 0.10) if config else 0.10
    
    async def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rank stocks based on analysis and fundamental data.
        
        Args:
            input_data: Dictionary with 'stock_data' and 'analyses' keys
            
        Returns:
            Dictionary with ranked stocks
        """
        self.validate_input(input_data, ["stock_data", "analyses"])
        
        stock_data = input_data["stock_data"]
        analyses = input_data["analyses"]
        
        self.log_execution(f"Ranking {len(stock_data)} stocks")
        
        # Calculate scores for each stock
        scored_stocks = []
        for symbol in stock_data.keys():
            if "error" in stock_data[symbol] or "error" in analyses.get(symbol, {}):
                continue
            
            score = self._calculate_score(
                symbol,
                stock_data[symbol],
                analyses.get(symbol, {})
            )
            
            if score is not None:
                scored_stocks.append({
                    "symbol": symbol,
                    "company_name": stock_data[symbol].get("company_name", "N/A"),
                    "score": score["total_score"],
                    "breakdown": score["breakdown"],
                    "fundamentals": self._extract_key_metrics(stock_data[symbol]),
                    "ai_recommendation": score.get("ai_recommendation", "N/A"),
                    "passes_screening": score["passes_screening"]
                })
        
        # Sort by score (descending)
        ranked_stocks = sorted(scored_stocks, key=lambda x: x["score"], reverse=True)
        
        # Filter stocks that pass screening criteria
        qualified_stocks = [s for s in ranked_stocks if s["passes_screening"]]
        
        self.log_execution(
            f"Ranked {len(ranked_stocks)} stocks, "
            f"{len(qualified_stocks)} passed screening criteria"
        )
        
        return {
            "agent": self.name,
            "total_stocks": len(ranked_stocks),
            "qualified_stocks": len(qualified_stocks),
            "ranked_stocks": ranked_stocks,
            "top_picks": qualified_stocks[:10]  # Top 10 qualified stocks
        }
    
    def _calculate_score(
        self,
        symbol: str,
        data: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Calculate a composite score for a stock.
        
        Args:
            symbol: Stock ticker
            data: Fundamental data
            analysis: AI analysis
            
        Returns:
            Dictionary with score breakdown or None if incomplete data
        """
        scores = {}
        
        # Growth Score (0-30 points)
        growth_score = self._score_growth(data)
        scores["growth"] = growth_score
        
        # Valuation Score (0-25 points)
        valuation_score = self._score_valuation(data)
        scores["valuation"] = valuation_score
        
        # Financial Health Score (0-20 points)
        financial_health_score = self._score_financial_health(data)
        scores["financial_health"] = financial_health_score
        
        # AI Analysis Score (0-25 points)
        ai_score, recommendation = self._score_ai_analysis(analysis)
        scores["ai_analysis"] = ai_score
        
        total_score = sum(scores.values())
        
        # Check if stock passes screening criteria
        passes_screening = self._check_screening_criteria(data)
        
        return {
            "total_score": total_score,
            "breakdown": scores,
            "ai_recommendation": recommendation,
            "passes_screening": passes_screening
        }
    
    def _score_growth(self, data: Dict[str, Any]) -> float:
        """Score based on growth metrics (0-30 points)."""
        score = 0.0
        
        # Revenue growth (0-15 points)
        revenue_growth = data.get("revenue_growth")
        if revenue_growth is not None:
            if revenue_growth >= 0.30:  # 30%+ growth
                score += 15
            elif revenue_growth >= 0.20:  # 20-30% growth
                score += 12
            elif revenue_growth >= 0.15:  # 15-20% growth
                score += 9
            elif revenue_growth >= 0.10:  # 10-15% growth
                score += 6
            elif revenue_growth >= 0:  # Positive growth
                score += 3
        
        # Earnings growth (0-15 points)
        earnings_growth = data.get("earnings_growth")
        if earnings_growth is not None:
            if earnings_growth >= 0.30:
                score += 15
            elif earnings_growth >= 0.20:
                score += 12
            elif earnings_growth >= 0.15:
                score += 9
            elif earnings_growth >= 0.10:
                score += 6
            elif earnings_growth >= 0:
                score += 3
        
        return score
    
    def _score_valuation(self, data: Dict[str, Any]) -> float:
        """Score based on valuation metrics (0-25 points)."""
        score = 0.0
        
        # P/E Ratio (0-10 points) - lower is better
        pe_ratio = data.get("pe_ratio")
        if pe_ratio is not None and pe_ratio > 0:
            if pe_ratio < 15:
                score += 10
            elif pe_ratio < 20:
                score += 7
            elif pe_ratio < 25:
                score += 5
            elif pe_ratio < 30:
                score += 3
        
        # PEG Ratio (0-10 points) - lower is better
        peg_ratio = data.get("peg_ratio")
        if peg_ratio is not None and peg_ratio > 0:
            if peg_ratio < 1.0:
                score += 10
            elif peg_ratio < 1.5:
                score += 7
            elif peg_ratio < 2.0:
                score += 5
            elif peg_ratio < 2.5:
                score += 3
        
        # Price relative to 52-week range (0-5 points)
        current_price = data.get("current_price", 0)
        low_52w = data.get("fifty_two_week_low", 0)
        high_52w = data.get("fifty_two_week_high", 1)
        
        if low_52w > 0 and high_52w > low_52w:
            price_position = (current_price - low_52w) / (high_52w - low_52w)
            if price_position < 0.3:  # In lower 30% of range
                score += 5
            elif price_position < 0.5:  # In lower 50% of range
                score += 3
        
        return score
    
    def _score_financial_health(self, data: Dict[str, Any]) -> float:
        """Score based on financial health metrics (0-20 points)."""
        score = 0.0
        
        # Profit margins (0-7 points)
        profit_margin = data.get("profit_margins")
        if profit_margin is not None:
            if profit_margin >= 0.20:
                score += 7
            elif profit_margin >= 0.15:
                score += 5
            elif profit_margin >= 0.10:
                score += 3
            elif profit_margin >= 0.05:
                score += 1
        
        # ROE (0-7 points)
        roe = data.get("roe")
        if roe is not None:
            if roe >= 0.20:
                score += 7
            elif roe >= 0.15:
                score += 5
            elif roe >= 0.10:
                score += 3
            elif roe >= 0.05:
                score += 1
        
        # Free cash flow positive (0-6 points)
        fcf = data.get("free_cash_flow", 0)
        if fcf > 0:
            score += 6
            # Bonus for strong FCF
            revenue = data.get("revenue", 0)
            if revenue > 0 and (fcf / revenue) >= 0.10:
                score += 2  # Extra points for 10%+ FCF margin
        
        return min(score, 20)  # Cap at 20 points
    
    def _score_ai_analysis(self, analysis: Dict[str, Any]) -> Tuple[float, str]:
        """Score based on AI analysis (0-25 points)."""
        if not analysis or "analysis" not in analysis:
            return 0.0, "N/A"
        
        analysis_text = analysis["analysis"].lower()
        recommendation = "Hold"
        score = 12.5  # Default neutral score
        
        # Extract recommendation
        if "strong buy" in analysis_text:
            recommendation = "Strong Buy"
            score = 25
        elif "buy" in analysis_text and "strong" not in analysis_text:
            recommendation = "Buy"
            score = 20
        elif "hold" in analysis_text:
            recommendation = "Hold"
            score = 12.5
        elif "sell" in analysis_text and "strong" not in analysis_text:
            recommendation = "Sell"
            score = 5
        elif "strong sell" in analysis_text:
            recommendation = "Strong Sell"
            score = 0
        
        # Try to extract growth score from AI analysis
        growth_score_match = re.search(r'growth\s*score[:\s]*(\d+(?:\.\d+)?)', analysis_text)
        if growth_score_match:
            ai_growth_score = float(growth_score_match.group(1))
            # Adjust score based on AI's growth rating (1-10 scale)
            score = min((ai_growth_score / 10) * 25, 25)  # Cap at 25 points
        
        return score, recommendation
    
    def _check_screening_criteria(self, data: Dict[str, Any]) -> bool:
        """Check if stock meets minimum screening criteria."""
        # Market cap check
        market_cap = data.get("market_cap", 0)
        if market_cap < self.min_market_cap:
            return False
        
        # P/E ratio check
        pe_ratio = data.get("pe_ratio")
        if pe_ratio is not None and pe_ratio > self.max_pe_ratio:
            return False
        
        # Revenue growth check
        revenue_growth = data.get("revenue_growth")
        if revenue_growth is None or revenue_growth < self.min_revenue_growth:
            return False
        
        # Earnings growth check
        earnings_growth = data.get("earnings_growth")
        if earnings_growth is None or earnings_growth < self.min_earnings_growth:
            return False
        
        return True
    
    @staticmethod
    def _extract_key_metrics(data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract key metrics for display."""
        return {
            "market_cap": data.get("market_cap", 0),
            "current_price": data.get("current_price", 0),
            "pe_ratio": data.get("pe_ratio"),
            "peg_ratio": data.get("peg_ratio"),
            "revenue_growth": data.get("revenue_growth"),
            "earnings_growth": data.get("earnings_growth"),
            "profit_margin": data.get("profit_margins"),
            "roe": data.get("roe")
        }
