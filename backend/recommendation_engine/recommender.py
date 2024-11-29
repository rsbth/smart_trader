from sklearn.preprocessing import MinMaxScaler
import numpy as np

class TradeRecommender:
    def __init__(self):
        self.scaler = MinMaxScaler()
        
        # Define weights for different analysis components
        self.weights = {
            'sentiment': 0.3,
            'technical': 0.4,
            'fundamental': 0.3
        }
    
    def get_recommendation(self, sentiment_data, technical_data, fundamental_data):
        # Calculate individual scores
        sentiment_score = self._calculate_sentiment_score(sentiment_data)
        technical_score = self._calculate_technical_score(technical_data)
        fundamental_score = self._calculate_fundamental_score(fundamental_data)
        
        # Calculate weighted average score
        final_score = (
            sentiment_score * self.weights['sentiment'] +
            technical_score * self.weights['technical'] +
            fundamental_score * self.weights['fundamental']
        )
        
        # Generate recommendation
        recommendation = self._generate_recommendation(final_score)
        
        return {
            'recommendation': recommendation['action'],
            'confidence': recommendation['confidence'],
            'target_price': recommendation['target_price'],
            'stop_loss': recommendation['stop_loss'],
            'scores': {
                'overall': final_score,
                'sentiment': sentiment_score,
                'technical': technical_score,
                'fundamental': fundamental_score
            }
        }
    
    def _calculate_sentiment_score(self, sentiment_data):
        if not sentiment_data:
            return 0.5
        
        overall_score = sentiment_data.get('overall_score', 0)
        # Convert from [-1, 1] to [0, 1] range
        return (overall_score + 1) / 2
    
    def _calculate_technical_score(self, technical_data):
        if not technical_data:
            return 0.5
        
        score = 0
        indicators = technical_data.get('indicators', {})
        
        # RSI analysis (0-100)
        rsi = indicators.get('rsi', 50)
        if rsi < 30:  # Oversold
            score += 1
        elif rsi > 70:  # Overbought
            score -= 1
        
        # MACD analysis
        macd = indicators.get('macd', {})
        if macd.get('macd', 0) > macd.get('signal', 0):
            score += 1
        else:
            score -= 1
        
        # Moving average analysis
        sma = indicators.get('sma', {})
        if sma.get('20', 0) > sma.get('50', 0):
            score += 1
        else:
            score -= 1
        
        # Normalize score to [0, 1] range
        return (score + 3) / 6
    
    def _calculate_fundamental_score(self, fundamental_data):
        if not fundamental_data:
            return 0.5
        
        score = 0
        
        # P/E ratio analysis
        pe_ratio = fundamental_data.get('pe_ratio', 0)
        if 0 < pe_ratio < 25:
            score += 1
        elif pe_ratio > 50:
            score -= 1
        
        # Revenue growth analysis
        revenue_growth = fundamental_data.get('revenue_growth', 0)
        if revenue_growth > 10:
            score += 1
        elif revenue_growth < 0:
            score -= 1
        
        # Profit margins analysis
        profit_margins = fundamental_data.get('profit_margins', 0)
        if profit_margins > 0.2:
            score += 1
        elif profit_margins < 0:
            score -= 1
        
        # Normalize score to [0, 1] range
        return (score + 3) / 6
    
    def _generate_recommendation(self, score):
        current_price = 100  # This should be fetched from real-time data
        
        if score >= 0.7:
            return {
                'action': 'BUY',
                'confidence': score,
                'target_price': current_price * 1.1,  # 10% profit target
                'stop_loss': current_price * 0.95  # 5% stop loss
            }
        elif score <= 0.3:
            return {
                'action': 'SELL',
                'confidence': 1 - score,
                'target_price': current_price * 0.9,  # 10% profit target
                'stop_loss': current_price * 1.05  # 5% stop loss
            }
        else:
            return {
                'action': 'HOLD',
                'confidence': 0.5,
                'target_price': current_price,
                'stop_loss': current_price * 0.95
            }
