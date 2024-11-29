import pytest
from backend.sentiment_analysis.analyzer import SentimentAnalyzer
from backend.technical_analysis.analyzer import TechnicalAnalyzer
from backend.fundamental_analysis.analyzer import FundamentalAnalyzer

def test_sentiment_analyzer():
    analyzer = SentimentAnalyzer()
    # Basic initialization test
    assert analyzer is not None

def test_technical_analyzer():
    analyzer = TechnicalAnalyzer()
    # Basic initialization test
    assert analyzer is not None
    
    # Test pattern detection methods
    candle = {
        'Open': 100,
        'Close': 105,
        'High': 110,
        'Low': 95
    }
    
    # Test doji pattern
    assert hasattr(analyzer, '_is_doji')
    
    # Test hammer pattern
    assert hasattr(analyzer, '_is_hammer')

def test_fundamental_analyzer():
    analyzer = FundamentalAnalyzer()
    # Basic initialization test
    assert analyzer is not None
    
    # Test metric calculation method exists
    assert hasattr(analyzer, '_calculate_metrics')
