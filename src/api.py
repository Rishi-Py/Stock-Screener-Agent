"""
Flask API server for the Stock Screener Agent.
"""

import os
import asyncio
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from loguru import logger

from src.agents.coordinator import MultiAgentCoordinator

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure logging
logger.add(
    "logs/screener_{time}.log",
    rotation="1 day",
    retention="7 days",
    level=os.getenv("LOG_LEVEL", "INFO")
)


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "service": "stock-screener-agent"})


@app.route('/api/screen', methods=['POST'])
def screen_stocks():
    """
    Screen stocks endpoint.
    
    Expected JSON body:
    {
        "symbols": ["AAPL", "MSFT", "GOOGL"],
        "batch_size": 5  // optional, default is 5
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'symbols' not in data:
            return jsonify({
                "error": "Missing required field 'symbols'"
            }), 400
        
        symbols = data['symbols']
        batch_size = data.get('batch_size', 5)
        
        if not isinstance(symbols, list) or len(symbols) == 0:
            return jsonify({
                "error": "Symbols must be a non-empty list"
            }), 400
        
        logger.info(f"Screening request received for {len(symbols)} symbols")
        
        # Initialize coordinator
        config = {
            "min_market_cap": int(os.getenv("MIN_MARKET_CAP", "1000000000")),
            "max_pe_ratio": float(os.getenv("MAX_PE_RATIO", "30")),
            "min_revenue_growth": float(os.getenv("MIN_REVENUE_GROWTH", "0.15")),
            "min_earnings_growth": float(os.getenv("MIN_EARNINGS_GROWTH", "0.10"))
        }
        
        coordinator = MultiAgentCoordinator(config)
        
        # Run the screening workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        if batch_size > 1:
            results = loop.run_until_complete(
                coordinator.screen_stocks_parallel(symbols, batch_size)
            )
        else:
            results = loop.run_until_complete(
                coordinator.screen_stocks(symbols)
            )
        
        loop.close()
        
        logger.info(f"Screening completed: {results['qualified_stocks']} qualified stocks")
        
        return jsonify(results)
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route('/api/screen/quick', methods=['POST'])
def quick_screen():
    """
    Quick screening endpoint with pre-defined growth stock universe.
    
    Expected JSON body:
    {
        "universe": "tech" | "growth" | "all"  // optional, default is "growth"
    }
    """
    try:
        data = request.get_json() or {}
        universe_type = data.get('universe', 'growth')
        
        # Pre-defined stock universes
        universes = {
            "tech": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
                "META", "TSLA", "AMD", "CRM", "ADBE"
            ],
            "growth": [
                "NVDA", "AMD", "SNOW", "PLTR", "NET",
                "CRWD", "DDOG", "ZS", "OKTA", "MDB"
            ],
            "all": [
                "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA",
                "META", "TSLA", "AMD", "CRM", "ADBE",
                "SNOW", "PLTR", "NET", "CRWD", "DDOG"
            ]
        }
        
        symbols = universes.get(universe_type, universes["growth"])
        
        logger.info(f"Quick screen requested for {universe_type} universe")
        
        # Initialize coordinator
        config = {
            "min_market_cap": int(os.getenv("MIN_MARKET_CAP", "1000000000")),
            "max_pe_ratio": float(os.getenv("MAX_PE_RATIO", "30")),
            "min_revenue_growth": float(os.getenv("MIN_REVENUE_GROWTH", "0.15")),
            "min_earnings_growth": float(os.getenv("MIN_EARNINGS_GROWTH", "0.10"))
        }
        
        coordinator = MultiAgentCoordinator(config)
        
        # Run the screening workflow
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        results = loop.run_until_complete(
            coordinator.screen_stocks_parallel(symbols, batch_size=5)
        )
        loop.close()
        
        return jsonify({
            "universe": universe_type,
            "results": results
        })
        
    except Exception as e:
        logger.error(f"Server error in quick screen: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    port = int(os.getenv('FLASK_PORT', 5000))
    logger.info(f"Starting Stock Screener Agent API on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
