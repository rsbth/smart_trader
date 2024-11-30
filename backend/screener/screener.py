import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from backend.technical_analysis.analyzer import TechnicalAnalyzer
from backend.broker_integration.broker import BrokerClient
import logging
import time

logger = logging.getLogger(__name__)

class StockScreener:
    def __init__(self, indices=None):
        self.analyzer = TechnicalAnalyzer()
        self.broker = BrokerClient()
        self.indices = indices or {
            'NIFTY50': '^NSEI',
            'NIFTYBANK': '^NSEBANK'
        }
        self.stocks = self._get_index_stocks()
        self.recommendations = []
        
    def _get_index_stocks(self):
        """Get all stocks from the configured indices"""
        stocks = set()
        for index_name, index_symbol in self.indices.items():
            try:
                index = yf.Ticker(index_symbol)
                # Get constituents if available
                if hasattr(index, 'constituents'):
                    stocks.update(index.constituents)
                else:
                    # Fallback to predefined lists if needed
                    stocks.update(self._get_predefined_stocks(index_name))
            except Exception as e:
                logger.error(f"Error fetching stocks for {index_name}: {e}")
        return list(stocks)
    
    def _get_predefined_stocks(self, index_name):
        """Fallback method for predefined stock lists"""
        if index_name == 'NIFTY50':
            return [
                'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'ICICIBANK.NS',
                'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS'
                # Add more stocks as needed
            ]
        elif index_name == 'NIFTYBANK':
            return [
                'HDFCBANK.NS', 'ICICIBANK.NS', 'KOTAKBANK.NS', 'AXISBANK.NS', 'SBIN.NS',
                'INDUSINDBK.NS', 'BANDHANBNK.NS', 'FEDERALBNK.NS', 'IDFCFIRSTB.NS', 'PNB.NS'
                # Add more stocks as needed
            ]
        return []

    def _analyze_stock(self, symbol):
        """Analyze a single stock and generate trading signals"""
        try:
            analysis = self.analyzer.analyze(symbol, period='1d', interval='5m')
            if not analysis:
                return None
            
            signals = self._generate_signals(symbol, analysis)
            if signals:
                return {
                    'symbol': symbol,
                    'signals': signals,
                    'analysis': analysis,
                    'timestamp': pd.Timestamp.now()
                }
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
        return None

    def _generate_signals(self, symbol, analysis):
        """Generate trading signals based on technical analysis"""
        signals = []
        
        # Get current market price
        current_price = analysis['current_price']
        
        # Check RSI conditions
        rsi = analysis['indicators']['rsi']
        if rsi['signal'] == 'oversold':
            signals.append({
                'type': 'BUY',
                'reason': f"RSI oversold ({rsi['value']:.2f})",
                'strength': 'medium'
            })
        elif rsi['signal'] == 'overbought':
            signals.append({
                'type': 'SELL',
                'reason': f"RSI overbought ({rsi['value']:.2f})",
                'strength': 'medium'
            })

        # Check MACD
        macd = analysis['indicators']['macd']
        if macd['histogram'] > 0 and abs(macd['histogram']) > abs(macd['histogram']) * 1.1:
            signals.append({
                'type': 'BUY',
                'reason': 'MACD bullish crossover',
                'strength': 'strong'
            })
        elif macd['histogram'] < 0 and abs(macd['histogram']) > abs(macd['histogram']) * 1.1:
            signals.append({
                'type': 'SELL',
                'reason': 'MACD bearish crossover',
                'strength': 'strong'
            })

        # Check Bollinger Bands
        bb = analysis['indicators']['bollinger_bands']
        if current_price <= bb['lower']:
            signals.append({
                'type': 'BUY',
                'reason': 'Price at Bollinger Band lower bound',
                'strength': 'medium'
            })
        elif current_price >= bb['upper']:
            signals.append({
                'type': 'SELL',
                'reason': 'Price at Bollinger Band upper bound',
                'strength': 'medium'
            })

        # Check candlestick patterns
        patterns = analysis['patterns']
        for pattern, value in patterns.items():
            if value:
                if pattern in ['hammer', 'morning_star'] or (pattern == 'engulfing' and value == 'bullish'):
                    signals.append({
                        'type': 'BUY',
                        'reason': f'Bullish pattern: {pattern}',
                        'strength': 'strong'
                    })
                elif pattern in ['shooting_star', 'evening_star'] or (pattern == 'engulfing' and value == 'bearish'):
                    signals.append({
                        'type': 'SELL',
                        'reason': f'Bearish pattern: {pattern}',
                        'strength': 'strong'
                    })

        # Trend analysis
        trend = analysis['indicators']['moving_averages']['trend']
        if trend in ['strong_uptrend', 'weak_uptrend']:
            signals.append({
                'type': 'BUY',
                'reason': f'Trend analysis: {trend}',
                'strength': 'weak' if 'weak' in trend else 'strong'
            })
        elif trend in ['strong_downtrend', 'weak_downtrend']:
            signals.append({
                'type': 'SELL',
                'reason': f'Trend analysis: {trend}',
                'strength': 'weak' if 'weak' in trend else 'strong'
            })

        return signals

    def screen_stocks(self):
        """Screen all stocks and generate recommendations"""
        logger.info(f"Starting stock screening for {len(self.stocks)} stocks")
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            results = list(executor.map(self._analyze_stock, self.stocks))
        
        # Filter out None results and sort by signal strength
        recommendations = [r for r in results if r and r['signals']]
        recommendations.sort(key=lambda x: self._calculate_signal_strength(x['signals']), reverse=True)
        
        self.recommendations = recommendations
        return recommendations

    def _calculate_signal_strength(self, signals):
        """Calculate overall signal strength"""
        strength_map = {'weak': 1, 'medium': 2, 'strong': 3}
        return sum(strength_map[s['strength']] for s in signals)

    def execute_recommendation(self, recommendation_id, action='BUY'):
        """Execute a trading recommendation"""
        try:
            rec = next((r for r in self.recommendations if r['id'] == recommendation_id), None)
            if not rec:
                raise ValueError(f"Recommendation {recommendation_id} not found")

            # Get the current market price
            symbol = rec['symbol']
            current_price = yf.Ticker(symbol).info.get('regularMarketPrice')
            
            # Execute the order through broker
            if action == 'BUY':
                order = self.broker.place_order(
                    symbol=symbol,
                    quantity=1,  # Calculate based on risk management
                    order_type='MARKET',
                    transaction_type='BUY'
                )
            else:
                order = self.broker.place_order(
                    symbol=symbol,
                    quantity=1,  # Calculate based on position size
                    order_type='MARKET',
                    transaction_type='SELL'
                )
            
            return {
                'status': 'success',
                'order_id': order['order_id'],
                'symbol': symbol,
                'action': action,
                'price': current_price,
                'timestamp': pd.Timestamp.now()
            }
            
        except Exception as e:
            logger.error(f"Error executing recommendation: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }

    def start_screening(self, interval_minutes=5):
        """Start continuous stock screening"""
        while True:
            try:
                recommendations = self.screen_stocks()
                logger.info(f"Found {len(recommendations)} trading opportunities")
                # You can implement notification system here
                
                # Wait for the next interval
                time.sleep(interval_minutes * 60)
            except Exception as e:
                logger.error(f"Error in screening loop: {e}")
                time.sleep(60)  # Wait a minute before retrying
