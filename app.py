from flask import Flask, request, jsonify, render_template
from backend.broker_integration.broker import broker
from backend.sentiment_analysis.analyzer import SentimentAnalyzer
from backend.technical_analysis.analyzer import TechnicalAnalyzer
from backend.fundamental_analysis.analyzer import FundamentalAnalyzer
from backend.recommendation_engine.recommender import TradeRecommender
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__,
    template_folder='frontend/templates',
    static_folder='frontend/static'
)
app.secret_key = os.urandom(24)

# Initialize analyzers
sentiment_analyzer = SentimentAnalyzer()
technical_analyzer = TechnicalAnalyzer()
fundamental_analyzer = FundamentalAnalyzer()
recommender = TradeRecommender()

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/v1/broker/login', methods=['POST'])
def login():
    """Login to Angel Broking"""
    success = broker.login()
    if success:
        return jsonify({
            'status': 'success',
            'message': 'Successfully logged in to Angel Broking'
        })
    return jsonify({
        'status': 'error',
        'message': 'Failed to login to Angel Broking'
    }), 401

@app.route('/api/v1/broker/profile')
def profile():
    """Get user profile"""
    if not broker.access_token:
        return jsonify({'error': 'Not authenticated'}), 401
    return jsonify(broker.get_profile())

@app.route('/api/v1/analyze', methods=['POST'])
def analyze():
    """Analyze a stock"""
    data = request.json
    if not data or 'symbol' not in data:
        return jsonify({'error': 'Symbol is required'}), 400

    symbol = data['symbol']
    
    # Perform analysis
    sentiment_score = sentiment_analyzer.analyze(symbol)
    technical_signals = technical_analyzer.analyze(symbol)
    fundamental_metrics = fundamental_analyzer.analyze(symbol)
    
    # Generate recommendation
    recommendation = recommender.get_recommendation(
        sentiment_score,
        technical_signals,
        fundamental_metrics
    )
    
    return jsonify({
        'symbol': symbol,
        'sentiment': sentiment_score,
        'technical': technical_signals,
        'fundamental': fundamental_metrics,
        'recommendation': recommendation
    })

@app.route('/api/v1/trade', methods=['POST'])
def trade():
    """Execute a trade"""
    if not broker.access_token:
        return jsonify({'error': 'Not authenticated'}), 401

    data = request.json
    if not data or not all(k in data for k in ['symbol', 'transaction_type', 'quantity']):
        return jsonify({'error': 'Missing required parameters'}), 400

    result = broker.execute_trade(
        data['symbol'],
        data['transaction_type'],
        data['quantity'],
        data.get('price')
    )
    return jsonify(result)

@app.route('/api/v1/portfolio')
def portfolio():
    """Get portfolio details"""
    if not broker.access_token:
        return jsonify({'error': 'Not authenticated'}), 401

    return jsonify({
        'holdings': broker.get_holdings(),
        'positions': broker.get_positions(),
        'funds': broker.get_funds()
    })

@app.route('/api/v1/orders')
def orders():
    """Get order book"""
    if not broker.access_token:
        return jsonify({'error': 'Not authenticated'}), 401

    return jsonify(broker.get_order_book())

@app.route('/api/v1/orders/<order_id>', methods=['DELETE'])
def cancel_order(order_id):
    """Cancel an order"""
    if not broker.access_token:
        return jsonify({'error': 'Not authenticated'}), 401

    result = broker.cancel_order(order_id)
    if result:
        return jsonify({'status': 'success', 'message': 'Order cancelled'})
    return jsonify({'status': 'error', 'message': 'Failed to cancel order'}), 400

@app.route('/api/v1/orders/webhook', methods=['POST'])
def webhook():
    """Handle Angel Broking postback notifications"""
    try:
        data = request.json
        # Log the webhook data
        app.logger.info(f"Received webhook data: {data}")
        
        # Process different types of notifications
        feed_type = data.get('feed_type')
        if feed_type == 'order':
            # Handle order updates
            order_id = data.get('order_id')
            status = data.get('status')
            app.logger.info(f"Order {order_id} status updated to {status}")
        elif feed_type == 'position':
            # Handle position updates
            symbol = data.get('trading_symbol')
            quantity = data.get('quantity')
            app.logger.info(f"Position update for {symbol}: quantity {quantity}")
            
        return jsonify({'status': 'success'})
    except Exception as e:
        app.logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
