"""
Command-line interface for the Stock Screener Agent.
"""

import asyncio
import argparse
import json
import os
from dotenv import load_dotenv
from loguru import logger
from tabulate import tabulate

from src.agents.coordinator import MultiAgentCoordinator

# Load environment variables
load_dotenv()


def format_results(results):
    """Format results for CLI display."""
    print("\n" + "=" * 80)
    print("STOCK SCREENING RESULTS")
    print("=" * 80)
    
    print(f"\nTotal Symbols Analyzed: {results['total_symbols']}")
    print(f"Stocks Ranked: {results['stocks_ranked']}")
    print(f"Qualified Stocks: {results['qualified_stocks']}")
    
    if results['top_picks']:
        print("\n" + "-" * 80)
        print("TOP PICKS")
        print("-" * 80)
        
        table_data = []
        for i, stock in enumerate(results['top_picks'][:10], 1):
            table_data.append([
                i,
                stock['symbol'],
                stock['company_name'][:30],
                f"{stock['score']:.2f}",
                stock['ai_recommendation'],
                f"{stock['fundamentals']['revenue_growth'] * 100:.1f}%" if stock['fundamentals']['revenue_growth'] else "N/A",
                f"{stock['fundamentals']['pe_ratio']:.1f}" if stock['fundamentals']['pe_ratio'] else "N/A"
            ])
        
        headers = ["Rank", "Symbol", "Company", "Score", "Recommendation", "Rev Growth", "P/E"]
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
    
    print("\n" + "=" * 80 + "\n")


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="AI-Powered Stock Screener Agent"
    )
    
    parser.add_argument(
        'symbols',
        nargs='+',
        help='Stock ticker symbols to screen (e.g., AAPL MSFT GOOGL)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=5,
        help='Number of stocks to process in parallel (default: 5)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for JSON results (optional)'
    )
    
    parser.add_argument(
        '--min-market-cap',
        type=float,
        help='Minimum market cap in billions (default: from .env or 1B)'
    )
    
    parser.add_argument(
        '--max-pe',
        type=float,
        help='Maximum P/E ratio (default: from .env or 30)'
    )
    
    args = parser.parse_args()
    
    # Build configuration
    config = {
        "min_market_cap": int(
            (args.min_market_cap * 1_000_000_000) if args.min_market_cap 
            else int(os.getenv("MIN_MARKET_CAP", "1000000000"))
        ),
        "max_pe_ratio": args.max_pe or float(os.getenv("MAX_PE_RATIO", "30")),
        "min_revenue_growth": float(os.getenv("MIN_REVENUE_GROWTH", "0.15")),
        "min_earnings_growth": float(os.getenv("MIN_EARNINGS_GROWTH", "0.10"))
    }
    
    logger.info(f"Screening {len(args.symbols)} stocks with batch size {args.batch_size}")
    
    # Initialize coordinator and run screening
    coordinator = MultiAgentCoordinator(config)
    
    if args.batch_size > 1:
        results = await coordinator.screen_stocks_parallel(
            args.symbols,
            args.batch_size
        )
    else:
        results = await coordinator.screen_stocks(args.symbols)
    
    # Display results
    format_results(results)
    
    # Save to file if requested
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Results saved to {args.output}")


if __name__ == '__main__':
    asyncio.run(main())
