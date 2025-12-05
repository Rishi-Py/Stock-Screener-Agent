"""
Example: Basic stock screening
"""

import asyncio
from src.agents.coordinator import MultiAgentCoordinator


async def main():
    """Basic example of screening stocks."""
    
    # Define stocks to screen
    symbols = ["AAPL", "MSFT", "GOOGL", "NVDA", "AMD"]
    
    # Initialize coordinator with default config
    coordinator = MultiAgentCoordinator()
    
    print(f"Screening {len(symbols)} stocks...")
    
    # Run screening
    results = await coordinator.screen_stocks(symbols)
    
    # Display results
    print(f"\nTotal stocks ranked: {results['stocks_ranked']}")
    print(f"Qualified stocks: {results['qualified_stocks']}")
    
    if results['top_picks']:
        print("\nTop 3 Picks:")
        for i, stock in enumerate(results['top_picks'][:3], 1):
            print(f"\n{i}. {stock['symbol']} - {stock['company_name']}")
            print(f"   Score: {stock['score']:.2f}")
            print(f"   Recommendation: {stock['ai_recommendation']}")
            print(f"   Revenue Growth: {stock['fundamentals']['revenue_growth'] * 100:.1f}%")


if __name__ == "__main__":
    asyncio.run(main())
