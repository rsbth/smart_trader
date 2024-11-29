import pytest
from unittest.mock import Mock, patch
from backend.sentiment_analysis.analyzer import SentimentAnalyzer
from backend.technical_analysis.analyzer import TechnicalAnalyzer
from backend.fundamental_analysis.analyzer import FundamentalAnalyzer

@pytest.fixture
def mock_newsapi():
    with patch('newsapi.NewsApiClient') as mock:
        yield mock

@pytest.fixture
def mock_twitter():
    with patch('tweepy.API') as mock:
        yield mock

@pytest.fixture
def mock_auth():
    with patch('tweepy.OAuthHandler') as mock:
        yield mock

class TestSentimentAnalyzer:
    def test_initialization(self, mock_newsapi, mock_twitter, mock_auth):
        analyzer = SentimentAnalyzer()
        assert analyzer is not None
        
    @patch('os.getenv')
    def test_analyze_with_no_data(self, mock_getenv, mock_newsapi, mock_twitter, mock_auth):
        mock_getenv.return_value = 'dummy_key'
        analyzer = SentimentAnalyzer()
        result = analyzer.analyze('AAPL')
        assert isinstance(result, dict)
        assert 'overall_score' in result

class TestTechnicalAnalyzer:
    def test_initialization(self):
        analyzer = TechnicalAnalyzer()
        assert analyzer is not None
    
    def test_pattern_detection(self):
        analyzer = TechnicalAnalyzer()
        candle = {
            'Open': 100,
            'Close': 105,
            'High': 110,
            'Low': 95
        }
        
        # Test doji pattern
        assert hasattr(analyzer, '_is_doji')
        result = analyzer._is_doji(candle)
        assert isinstance(result, bool)
        
        # Test hammer pattern
        assert hasattr(analyzer, '_is_hammer')
        result = analyzer._is_hammer(candle)
        assert isinstance(result, bool)

class TestFundamentalAnalyzer:
    def test_initialization(self):
        analyzer = FundamentalAnalyzer()
        assert analyzer is not None
    
    @patch('yfinance.Ticker')
    def test_analyze_with_mock_data(self, mock_ticker):
        # Mock the yfinance Ticker object
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = {
            'marketCap': 1000000,
            'trailingPE': 20,
            'forwardPE': 18,
            'priceToBook': 3,
        }
        mock_ticker_instance.quarterly_financials = Mock()
        mock_ticker_instance.quarterly_financials.empty = True
        mock_ticker.return_value = mock_ticker_instance
        
        analyzer = FundamentalAnalyzer()
        result = analyzer.analyze('AAPL')
        
        assert isinstance(result, dict)
        assert 'market_cap' in result
        assert result['market_cap'] == 1000000
