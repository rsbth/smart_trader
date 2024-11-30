from flask import Flask, jsonify, request
from flask_cors import CORS
from backend.screener.screener import StockScreener
from backend.recommendations.engine import RecommendationEngine
import threading
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__, 
            static_folder='../frontend/static',
            template_folder='../frontend/templates')
CORS(app)

# Initialize components
screener = StockScreener()
recommendation_engine = RecommendationEngine()

# Start background screening
def run_screener():
    while True:
        try:
            # Screen stocks and process recommendations
            screening_results = screener.screen_stocks()
            recommendation_engine.process_signals(screening_results)
            logger.info(f"Completed screening cycle. Found {len(screening_results)} signals")
        except Exception as e:
            logger.error(f"Error in screening cycle: {e}")

@app.route('/')
def index():
    return app.send_from_directory(app.template_folder, 'index.html')

@app.route('/api/recommendations')
def get_recommendations():
    recommendations = recommendation_engine.get_active_recommendations()
    return jsonify(recommendations)

@app.route('/api/positions')
def get_positions():
    try:
        positions = recommendation_engine.broker.get_positions()
        return jsonify(positions)
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        return jsonify([])

@app.route('/api/recent-trades')
def get_recent_trades():
    trades = recommendation_engine.get_executed_trades()
    return jsonify(trades)

@app.route('/api/portfolio')
def get_portfolio():
    try:
        value = recommendation_engine.broker.get_portfolio_value()
        return jsonify({'value': value})
    except Exception as e:
        logger.error(f"Error fetching portfolio value: {e}")
        return jsonify({'value': 0})

@app.route('/api/execute-trade', methods=['POST'])
def execute_trade():
    try:
        data = request.get_json()
        recommendation_id = data.get('recommendation_id')
        if not recommendation_id:
            return jsonify({'status': 'error', 'error': 'Missing recommendation_id'})
        
        result = recommendation_engine.execute_recommendation(recommendation_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error executing trade: {e}")
        return jsonify({'status': 'error', 'error': str(e)})

def main():
    try:
        # Start the screener in a background thread
        screener_thread = threading.Thread(target=run_screener, daemon=True)
        screener_thread.start()
        
        # Start the Flask application
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
    except Exception as e:
        logger.error(f"Error starting application: {e}")
        raise

if __name__ == '__main__':
    main()
