from flask import Flask, render_template, jsonify, request
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__, 
    template_folder='frontend/templates',
    static_folder='frontend/static'
)

# Import analysis modules (to be implemented)
from backend.sentiment_analysis.analyzer import SentimentAnalyzer
from backend.technical_analysis.analyzer import TechnicalAnalyzer
from backend.fundamental_analysis.analyzer import FundamentalAnalyzer
from backend.recommendation_engine.recommender import TradeRecommender

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_stock():
    data = request.get_json()
    symbol = data.get('symbol')
    
    # Initialize analyzers
    sentiment = SentimentAnalyzer()
    technical = TechnicalAnalyzer()
    fundamental = FundamentalAnalyzer()
    recommender = TradeRecommender()
    
    # Perform analysis
    sentiment_score = sentiment.analyze(symbol)
    technical_signals = technical.analyze(symbol)
    fundamental_metrics = fundamental.analyze(symbol)
    
    # Generate recommendation
    recommendation = recommender.get_recommendation(
        sentiment_score,
        technical_signals,
        fundamental_metrics
    )
    
    return jsonify({
        'symbol': symbol,
        'sentiment_analysis': sentiment_score,
        'technical_analysis': technical_signals,
        'fundamental_analysis': fundamental_metrics,
        'recommendation': recommendation
    })

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    data = request.get_json()
    # Implement trade execution logic here
    return jsonify({'status': 'success', 'message': 'Trade executed'})

if __name__ == '__main__':
    app.run(debug=True)
