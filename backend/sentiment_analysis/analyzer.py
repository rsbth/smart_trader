import os
from textblob import TextBlob
from newsapi import NewsApiClient
import tweepy
from datetime import datetime, timedelta

class SentimentAnalyzer:
    def __init__(self):
        # Initialize API clients
        self.newsapi = NewsApiClient(api_key=os.getenv('NEWS_API_KEY'))
        
        # Twitter API setup
        auth = tweepy.OAuthHandler(
            os.getenv('TWITTER_API_KEY'),
            os.getenv('TWITTER_API_SECRET')
        )
        self.twitter_api = tweepy.API(auth)
    
    def analyze(self, symbol):
        news_sentiment = self._analyze_news(symbol)
        social_sentiment = self._analyze_social_media(symbol)
        
        # Combine sentiments with weighted average
        combined_sentiment = (news_sentiment * 0.6) + (social_sentiment * 0.4)
        
        return {
            'overall_score': combined_sentiment,
            'news_sentiment': news_sentiment,
            'social_sentiment': social_sentiment
        }
    
    def _analyze_news(self, symbol):
        try:
            # Get news articles from last 7 days
            articles = self.newsapi.get_everything(
                q=symbol,
                language='en',
                from_param=(datetime.now() - timedelta(days=7)).date(),
                to=datetime.now().date()
            )
            
            if not articles['articles']:
                return 0
            
            # Analyze sentiment of each article
            sentiments = []
            for article in articles['articles']:
                text = f"{article['title']} {article['description']}"
                blob = TextBlob(text)
                sentiments.append(blob.sentiment.polarity)
            
            return sum(sentiments) / len(sentiments)
        
        except Exception as e:
            print(f"Error analyzing news: {str(e)}")
            return 0
    
    def _analyze_social_media(self, symbol):
        try:
            # Get recent tweets
            tweets = self.twitter_api.search_tweets(
                q=symbol,
                lang='en',
                count=100
            )
            
            if not tweets:
                return 0
            
            # Analyze sentiment of each tweet
            sentiments = []
            for tweet in tweets:
                blob = TextBlob(tweet.text)
                sentiments.append(blob.sentiment.polarity)
            
            return sum(sentiments) / len(sentiments)
        
        except Exception as e:
            print(f"Error analyzing social media: {str(e)}")
            return 0
