"""
Multi-Agent Coordinator - Orchestrates the agent workflow.
"""

import asyncio
from typing import Any, Dict, List, Optional
from loguru import logger

from .data_fetcher import DataFetcherAgent
from .analysis_agent import AnalysisAgent
from .ranking_agent import RankingAgent


class MultiAgentCoordinator:
    """Coordinates the execution of multiple agents in the screening workflow."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the coordinator with all agents.
        
        Args:
            config: Configuration dictionary for agents
        """
        self.config = config or {}
        
        # Initialize agents
        self.data_fetcher = DataFetcherAgent(config)
        self.analysis_agent = AnalysisAgent(config)
        self.ranking_agent = RankingAgent(config)
        
        logger.info("Multi-Agent Coordinator initialized")
    
    async def screen_stocks(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Execute the complete stock screening workflow.
        
        Args:
            symbols: List of stock ticker symbols to screen
            
        Returns:
            Dictionary with complete screening results
        """
        logger.info(f"Starting stock screening workflow for {len(symbols)} symbols")
        
        try:
            # Step 1: Fetch fundamental data
            logger.info("Step 1: Fetching fundamental data...")
            fetch_result = await self.data_fetcher.execute({"symbols": symbols})
            stock_data = fetch_result["data"]
            
            # Step 2: AI-powered analysis
            logger.info("Step 2: Performing AI analysis...")
            analysis_result = await self.analysis_agent.execute({"stock_data": stock_data})
            analyses = analysis_result["analyses"]
            
            # Step 3: Rank stocks
            logger.info("Step 3: Ranking stocks...")
            ranking_result = await self.ranking_agent.execute({
                "stock_data": stock_data,
                "analyses": analyses
            })
            
            # Compile final results
            results = {
                "workflow": "complete",
                "total_symbols": len(symbols),
                "data_fetched": fetch_result["symbols_processed"],
                "stocks_analyzed": analysis_result["stocks_analyzed"],
                "stocks_ranked": ranking_result["total_stocks"],
                "qualified_stocks": ranking_result["qualified_stocks"],
                "top_picks": ranking_result["top_picks"],
                "all_rankings": ranking_result["ranked_stocks"]
            }
            
            logger.info(
                f"Workflow complete: {results['qualified_stocks']} qualified stocks, "
                f"top pick: {results['top_picks'][0]['symbol'] if results['top_picks'] else 'None'}"
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in screening workflow: {str(e)}")
            raise
    
    async def screen_stocks_parallel(
        self,
        symbols: List[str],
        batch_size: int = 5
    ) -> Dict[str, Any]:
        """
        Execute screening workflow with parallel processing for better performance.
        
        Args:
            symbols: List of stock ticker symbols to screen
            batch_size: Number of stocks to process in parallel
            
        Returns:
            Dictionary with complete screening results
        """
        logger.info(
            f"Starting parallel stock screening for {len(symbols)} symbols "
            f"(batch size: {batch_size})"
        )
        
        all_stock_data = {}
        all_analyses = {}
        
        # Process in batches
        for i in range(0, len(symbols), batch_size):
            batch = symbols[i:i + batch_size]
            logger.info(f"Processing batch {i // batch_size + 1}: {batch}")
            
            # Fetch data for batch
            fetch_result = await self.data_fetcher.execute({"symbols": batch})
            all_stock_data.update(fetch_result["data"])
            
            # Analyze batch
            analysis_result = await self.analysis_agent.execute({
                "stock_data": fetch_result["data"]
            })
            all_analyses.update(analysis_result["analyses"])
        
        # Rank all stocks together
        ranking_result = await self.ranking_agent.execute({
            "stock_data": all_stock_data,
            "analyses": all_analyses
        })
        
        results = {
            "workflow": "parallel_complete",
            "total_symbols": len(symbols),
            "batch_size": batch_size,
            "stocks_ranked": ranking_result["total_stocks"],
            "qualified_stocks": ranking_result["qualified_stocks"],
            "top_picks": ranking_result["top_picks"],
            "all_rankings": ranking_result["ranked_stocks"]
        }
        
        logger.info(f"Parallel workflow complete: {results['qualified_stocks']} qualified stocks")
        
        return results
