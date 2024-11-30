import yfinance as yf
import pandas as pd
import numpy as np
import ta
from ta.volatility import BollingerBands, AverageTrueRange
from ta.momentum import StochasticOscillator
from ta.trend import ADXIndicator
from ta.volume import OnBalanceVolumeIndicator, AccDistIndexIndicator

class TechnicalAnalyzer:
    def __init__(self):
        self.patterns = {
            'hammer': self._is_hammer,
            'shooting_star': self._is_shooting_star,
            'doji': self._is_doji,
            'engulfing': self._is_engulfing,
            'morning_star': self._is_morning_star,
            'evening_star': self._is_evening_star
        }
    
    def analyze(self, symbol, period='1y', interval='1d'):
        # Get historical data
        stock = yf.Ticker(symbol)
        df = stock.history(period=period, interval=interval)
        
        if df.empty:
            return None
        
        # Calculate technical indicators
        indicators = self._calculate_indicators(df)
        
        # Identify patterns
        patterns = self._identify_patterns(df)
        
        # Find support and resistance levels
        levels = self._find_support_resistance(df)
        
        # Calculate Fibonacci levels
        fib_levels = self._calculate_fibonacci_levels(df)
        
        return {
            'indicators': indicators,
            'patterns': patterns,
            'support_resistance': levels,
            'fibonacci_levels': fib_levels,
            'current_price': df['Close'].iloc[-1],
            'summary': self._generate_analysis_summary(indicators, patterns)
        }
    
    def _calculate_indicators(self, df):
        # RSI
        rsi = ta.momentum.RSIIndicator(df['Close']).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        
        # Moving averages
        sma_20 = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
        sma_50 = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
        sma_200 = ta.trend.SMAIndicator(df['Close'], window=200).sma_indicator()
        
        # Bollinger Bands
        bb = BollingerBands(df['Close'])
        
        # ATR for volatility
        atr = AverageTrueRange(df['High'], df['Low'], df['Close'])
        
        # Stochastic Oscillator
        stoch = StochasticOscillator(df['High'], df['Low'], df['Close'])
        
        # ADX for trend strength
        adx = ADXIndicator(df['High'], df['Low'], df['Close'])
        
        # Volume indicators
        obv = OnBalanceVolumeIndicator(df['Close'], df['Volume'])
        adi = AccDistIndexIndicator(df['High'], df['Low'], df['Close'], df['Volume'])
        
        return {
            'rsi': {
                'value': rsi.iloc[-1],
                'signal': 'oversold' if rsi.iloc[-1] < 30 else 'overbought' if rsi.iloc[-1] > 70 else 'neutral'
            },
            'macd': {
                'macd': macd.macd().iloc[-1],
                'signal': macd.macd_signal().iloc[-1],
                'histogram': macd.macd_diff().iloc[-1]
            },
            'moving_averages': {
                'sma_20': sma_20.iloc[-1],
                'sma_50': sma_50.iloc[-1],
                'sma_200': sma_200.iloc[-1],
                'trend': self._determine_trend(sma_20.iloc[-1], sma_50.iloc[-1], sma_200.iloc[-1])
            },
            'bollinger_bands': {
                'upper': bb.bollinger_hband().iloc[-1],
                'middle': bb.bollinger_mavg().iloc[-1],
                'lower': bb.bollinger_lband().iloc[-1],
                'width': bb.bollinger_wband().iloc[-1]
            },
            'volatility': {
                'atr': atr.average_true_range().iloc[-1],
                'atr_percent': (atr.average_true_range().iloc[-1] / df['Close'].iloc[-1]) * 100
            },
            'stochastic': {
                'k': stoch.stoch().iloc[-1],
                'd': stoch.stoch_signal().iloc[-1]
            },
            'trend_strength': {
                'adx': adx.adx().iloc[-1],
                'strength': self._interpret_adx(adx.adx().iloc[-1])
            },
            'volume': {
                'obv': obv.on_balance_volume().iloc[-1],
                'adi': adi.acc_dist_index().iloc[-1],
                'volume_sma': df['Volume'].rolling(window=20).mean().iloc[-1]
            }
        }
    
    def _determine_trend(self, sma20, sma50, sma200):
        if sma20 > sma50 > sma200:
            return 'strong_uptrend'
        elif sma20 > sma50 and sma50 < sma200:
            return 'weak_uptrend'
        elif sma20 < sma50 < sma200:
            return 'strong_downtrend'
        elif sma20 < sma50 and sma50 > sma200:
            return 'weak_downtrend'
        return 'sideways'
    
    def _interpret_adx(self, adx):
        if adx >= 50:
            return 'very_strong'
        elif adx >= 25:
            return 'strong'
        elif adx >= 20:
            return 'moderate'
        return 'weak'
    
    def _identify_patterns(self, df):
        patterns_found = {}
        last_candles = df.iloc[-3:]  # Get last 3 candles for pattern recognition
        
        for pattern_name, pattern_func in self.patterns.items():
            if pattern_name in ['morning_star', 'evening_star']:
                patterns_found[pattern_name] = pattern_func(last_candles)
            else:
                patterns_found[pattern_name] = pattern_func(df.iloc[-1])
        return patterns_found
    
    def _find_support_resistance(self, df, window=20):
        levels = []
        
        for i in range(window, len(df)):
            high_level = df['High'].iloc[i-window:i].max()
            low_level = df['Low'].iloc[i-window:i].min()
            
            if len(levels) == 0:
                levels.extend([low_level, high_level])
            else:
                # Check if level is significantly different from existing levels
                for level in [low_level, high_level]:
                    if not any(abs(level - existing) < (level * 0.02) for existing in levels):
                        levels.append(level)
        
        return sorted(levels)
    
    def _calculate_fibonacci_levels(self, df):
        high = df['High'].max()
        low = df['Low'].min()
        diff = high - low
        
        return {
            '0': low,
            '0.236': low + 0.236 * diff,
            '0.382': low + 0.382 * diff,
            '0.5': low + 0.5 * diff,
            '0.618': low + 0.618 * diff,
            '0.786': low + 0.786 * diff,
            '1': high
        }
    
    def _is_hammer(self, candle):
        body = abs(candle['Open'] - candle['Close'])
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        return (lower_shadow > 2 * body) and (upper_shadow < body)
    
    def _is_shooting_star(self, candle):
        body = abs(candle['Open'] - candle['Close'])
        lower_shadow = min(candle['Open'], candle['Close']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Open'], candle['Close'])
        
        return (upper_shadow > 2 * body) and (lower_shadow < body)
    
    def _is_doji(self, candle):
        body = abs(candle['Open'] - candle['Close'])
        total_range = candle['High'] - candle['Low']
        
        return body <= (total_range * 0.1)
    
    def _is_engulfing(self, candle):
        prev_candle = candle.shift(1)
        
        bullish = (prev_candle['Close'] < prev_candle['Open'] and  # Previous red
                  candle['Close'] > candle['Open'] and  # Current green
                  candle['Open'] < prev_candle['Close'] and  # Opens below prev close
                  candle['Close'] > prev_candle['Open'])  # Closes above prev open
        
        bearish = (prev_candle['Close'] > prev_candle['Open'] and  # Previous green
                  candle['Close'] < candle['Open'] and  # Current red
                  candle['Open'] > prev_candle['Close'] and  # Opens above prev close
                  candle['Close'] < prev_candle['Open'])  # Closes below prev open
        
        return 'bullish' if bullish else 'bearish' if bearish else None
    
    def _is_morning_star(self, candles):
        if len(candles) < 3:
            return False
            
        first_body = candles.iloc[0]['Close'] - candles.iloc[0]['Open']
        second_body = abs(candles.iloc[1]['Close'] - candles.iloc[1]['Open'])
        third_body = candles.iloc[2]['Close'] - candles.iloc[2]['Open']
        
        return (first_body < 0 and  # First day is red
                second_body < abs(first_body) * 0.3 and  # Second day is small
                third_body > 0 and  # Third day is green
                third_body > abs(first_body) * 0.5)  # Third day covers significant part of first day
    
    def _is_evening_star(self, candles):
        if len(candles) < 3:
            return False
            
        first_body = candles.iloc[0]['Close'] - candles.iloc[0]['Open']
        second_body = abs(candles.iloc[1]['Close'] - candles.iloc[1]['Open'])
        third_body = candles.iloc[2]['Close'] - candles.iloc[2]['Open']
        
        return (first_body > 0 and  # First day is green
                second_body < first_body * 0.3 and  # Second day is small
                third_body < 0 and  # Third day is red
                abs(third_body) > first_body * 0.5)  # Third day covers significant part of first day
    
    def _generate_analysis_summary(self, indicators, patterns):
        summary = []
        
        # Trend analysis
        trend = indicators['moving_averages']['trend']
        summary.append(f"Overall Trend: {trend.replace('_', ' ').title()}")
        
        # RSI analysis
        rsi = indicators['rsi']
        summary.append(f"RSI ({rsi['value']:.2f}) indicates {rsi['signal']} conditions")
        
        # MACD analysis
        macd = indicators['macd']
        macd_signal = "bullish" if macd['histogram'] > 0 else "bearish"
        summary.append(f"MACD shows {macd_signal} momentum")
        
        # Trend strength
        trend_strength = indicators['trend_strength']
        summary.append(f"Trend Strength (ADX): {trend_strength['strength'].replace('_', ' ').title()}")
        
        # Volume analysis
        vol_sma = indicators['volume']['volume_sma']
        current_vol = indicators['volume']['obv']
        vol_signal = "above" if current_vol > vol_sma else "below"
        summary.append(f"Volume is {vol_signal} 20-day average")
        
        # Pattern analysis
        active_patterns = [k for k, v in patterns.items() if v]
        if active_patterns:
            summary.append(f"Detected patterns: {', '.join(active_patterns)}")
        
        return summary
