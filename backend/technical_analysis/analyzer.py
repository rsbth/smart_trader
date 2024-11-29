import yfinance as yf
import pandas as pd
import numpy as np
import ta

class TechnicalAnalyzer:
    def __init__(self):
        self.patterns = {
            'hammer': self._is_hammer,
            'shooting_star': self._is_shooting_star,
            'doji': self._is_doji
        }
    
    def analyze(self, symbol):
        # Get historical data
        stock = yf.Ticker(symbol)
        df = stock.history(period='1y')
        
        if df.empty:
            return None
        
        # Calculate technical indicators
        indicators = self._calculate_indicators(df)
        
        # Identify patterns
        patterns = self._identify_patterns(df)
        
        # Find support and resistance levels
        levels = self._find_support_resistance(df)
        
        return {
            'indicators': indicators,
            'patterns': patterns,
            'support_resistance': levels
        }
    
    def _calculate_indicators(self, df):
        # RSI
        rsi = ta.momentum.RSIIndicator(df['Close']).rsi()
        
        # MACD
        macd = ta.trend.MACD(df['Close'])
        
        # Moving averages
        sma_20 = ta.trend.SMAIndicator(df['Close'], window=20).sma_indicator()
        sma_50 = ta.trend.SMAIndicator(df['Close'], window=50).sma_indicator()
        
        return {
            'rsi': rsi.iloc[-1],
            'macd': {
                'macd': macd.macd().iloc[-1],
                'signal': macd.macd_signal().iloc[-1]
            },
            'sma': {
                '20': sma_20.iloc[-1],
                '50': sma_50.iloc[-1]
            }
        }
    
    def _identify_patterns(self, df):
        patterns_found = {}
        for pattern_name, pattern_func in self.patterns.items():
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
