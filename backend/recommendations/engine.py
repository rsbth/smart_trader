import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from backend.broker_integration.broker import BrokerClient
from backend.risk_management.calculator import RiskCalculator

logger = logging.getLogger(__name__)

class RecommendationEngine:
    def __init__(self):
        self.broker = BrokerClient()
        self.risk_calculator = RiskCalculator()
        self.active_recommendations = []
        self.executed_trades = []
        self.max_active_trades = 5
        self.max_position_size = 0.1  # 10% of portfolio per trade
        
    def process_signals(self, screening_results):
        """Process screening results and generate actionable recommendations"""
        current_positions = self.broker.get_positions()
        portfolio_value = self.broker.get_portfolio_value()
        
        recommendations = []
        for result in screening_results:
            try:
                recommendation = self._create_recommendation(
                    result, 
                    current_positions,
                    portfolio_value
                )
                if recommendation:
                    recommendations.append(recommendation)
            except Exception as e:
                logger.error(f"Error processing signal for {result['symbol']}: {e}")
        
        # Sort recommendations by priority
        recommendations.sort(key=lambda x: x['priority'], reverse=True)
        
        # Update active recommendations
        self.active_recommendations = recommendations
        return recommendations
    
    def _create_recommendation(self, screening_result, current_positions, portfolio_value):
        """Create a trading recommendation based on screening results and current positions"""
        symbol = screening_result['symbol']
        signals = screening_result['signals']
        analysis = screening_result['analysis']
        
        # Determine overall signal direction and strength
        buy_signals = [s for s in signals if s['type'] == 'BUY']
        sell_signals = [s for s in signals if s['type'] == 'SELL']
        
        # Calculate signal scores
        buy_score = sum(self._get_strength_score(s['strength']) for s in buy_signals)
        sell_score = sum(self._get_strength_score(s['strength']) for s in sell_signals)
        
        # Check if we have a position in this stock
        current_position = next((p for p in current_positions if p['symbol'] == symbol), None)
        
        recommendation = {
            'id': f"REC_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'symbol': symbol,
            'timestamp': pd.Timestamp.now(),
            'signals': signals,
            'analysis': analysis
        }
        
        if current_position:
            # We have a position, check for exit
            if sell_score > buy_score and sell_score >= 2:
                recommendation.update({
                    'action': 'SELL',
                    'type': 'EXIT',
                    'quantity': current_position['quantity'],
                    'priority': sell_score,
                    'reasons': [s['reason'] for s in sell_signals],
                    'risk_level': 'LOW' if sell_score > 4 else 'MEDIUM'
                })
                return recommendation
        else:
            # No position, check for entry
            if buy_score > sell_score and buy_score >= 2:
                # Calculate position size
                risk_params = self.risk_calculator.calculate_risk_parameters(
                    symbol,
                    portfolio_value,
                    analysis
                )
                
                if risk_params['risk_level'] in ['LOW', 'MEDIUM']:
                    recommendation.update({
                        'action': 'BUY',
                        'type': 'ENTRY',
                        'quantity': risk_params['suggested_quantity'],
                        'priority': buy_score,
                        'reasons': [s['reason'] for s in buy_signals],
                        'risk_level': risk_params['risk_level'],
                        'stop_loss': risk_params['stop_loss'],
                        'target': risk_params['target']
                    })
                    return recommendation
        
        return None
    
    def _get_strength_score(self, strength):
        """Convert strength label to numeric score"""
        return {'weak': 1, 'medium': 2, 'strong': 3}.get(strength, 0)
    
    def execute_recommendation(self, recommendation_id):
        """Execute a trading recommendation"""
        rec = next((r for r in self.active_recommendations if r['id'] == recommendation_id), None)
        if not rec:
            raise ValueError(f"Recommendation {recommendation_id} not found")
        
        try:
            # Place the order
            order = self.broker.place_order(
                symbol=rec['symbol'],
                quantity=rec['quantity'],
                order_type='MARKET',
                transaction_type=rec['action'],
                stop_loss=rec.get('stop_loss'),
                target=rec.get('target')
            )
            
            # Record the executed trade
            trade_record = {
                'recommendation_id': rec['id'],
                'order_id': order['order_id'],
                'symbol': rec['symbol'],
                'action': rec['action'],
                'quantity': rec['quantity'],
                'timestamp': pd.Timestamp.now(),
                'status': 'EXECUTED'
            }
            self.executed_trades.append(trade_record)
            
            # Remove from active recommendations
            self.active_recommendations = [r for r in self.active_recommendations if r['id'] != recommendation_id]
            
            return {
                'status': 'success',
                'trade': trade_record
            }
            
        except Exception as e:
            logger.error(f"Error executing recommendation {recommendation_id}: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def get_active_recommendations(self):
        """Get current active recommendations"""
        # Clean up old recommendations
        current_time = pd.Timestamp.now()
        self.active_recommendations = [
            r for r in self.active_recommendations
            if current_time - r['timestamp'] < pd.Timedelta(hours=1)
        ]
        return self.active_recommendations
    
    def get_executed_trades(self, start_date=None, end_date=None):
        """Get executed trades history"""
        trades = self.executed_trades
        if start_date:
            trades = [t for t in trades if t['timestamp'] >= pd.Timestamp(start_date)]
        if end_date:
            trades = [t for t in trades if t['timestamp'] <= pd.Timestamp(end_date)]
        return trades
