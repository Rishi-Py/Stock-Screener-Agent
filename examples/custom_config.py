"""
Example: Custom configuration screening
"""

import asyncio
from src.agents.coordinator import MultiAgentCoordinator


async def main():
    """Example with custom screening configuration."""
    
    # Custom configuration
    config = {
        "min_market_cap": 5_000_000_000,  # 5B minimum
        "max_pe_ratio": 25,  # Lower P/E threshold
        "min_revenue_growth": 0.20,  # 20% minimum revenue growth
        "min_earnings_growth": 0.15  # 15% minimum earnings growth
    }
    
    # High-growth tech stocks
    symbols = [
        "NVDA", "AMD", "SNOW", "PLTR", "NET",
        "CRWD", "DDOG", "ZS", "OKTA", "MDB"
    ]
    
    print("Custom Screening Configuration:")
    print(f"  Min Market Cap: ${config['min_market_cap']:,}")
    print(f"  Max P/E Ratio: {config['max_pe_ratio']}")
    print(f"  Min Revenue Growth: {config['min_revenue_growth'] * 100}%")
    print(f"  Min Earnings Growth: {config['min_earnings_growth'] * 100}%")
    print()
    
    # Initialize coordinator with custom config
    coordinator = MultiAgentCoordinator(config)
    
    # Use parallel processing for faster results
    results = await coordinator.screen_stocks_parallel(
        symbols,
        batch_size=5
    )
    
    # Display results
    print(f"\nScreening Complete!")
    print(f"Total stocks analyzed: {results['total_symbols']}")
    print(f"Qualified stocks: {results['qualified_stocks']}")
    
    if results['top_picks']:
        print("\n" + "="*80)
        print("TOP QUALIFIED STOCKS")
        print("="*80)
        
        for i, stock in enumerate(results['top_picks'], 1):
            print(f"\n{i}. {stock['symbol']} - {stock['company_name']}")
            print(f"   Overall Score: {stock['score']:.2f}/100")
            print(f"   AI Recommendation: {stock['ai_recommendation']}")
            
            # Score breakdown
            breakdown = stock['breakdown']
            print(f"   Score Breakdown:")
            print(f"     - Growth: {breakdown['growth']:.1f}/30")
            print(f"     - Valuation: {breakdown['valuation']:.1f}/25")
            print(f"     - Financial Health: {breakdown['financial_health']:.1f}/20")
            print(f"     - AI Analysis: {breakdown['ai_analysis']:.1f}/25")
            
            # Key metrics
            metrics = stock['fundamentals']
            print(f"   Key Metrics:")
            if metrics.get('revenue_growth') is not None:
                print(f"     - Revenue Growth: {metrics['revenue_growth'] * 100:.1f}%")
            else:
                print(f"     - Revenue Growth: N/A")
            print(f"     - P/E Ratio: {metrics['pe_ratio']:.1f}" if metrics['pe_ratio'] else "     - P/E Ratio: N/A")
            print(f"     - Profit Margin: {metrics['profit_margin'] * 100:.1f}%" if metrics['profit_margin'] else "     - Profit Margin: N/A")
    else:
        print("\nNo stocks met the screening criteria.")


if __name__ == "__main__":
    asyncio.run(main())
