# Smart Trader

A comprehensive trading application that provides intelligent trading recommendations based on multiple analysis factors:

1. Sentiment Analysis
   - Social media sentiment
   - News sentiment
   - Overall market sentiment

2. Technical Analysis
   - Candlestick patterns
   - Support and resistance levels
   - Moving averages
   - Technical indicators

3. Fundamental Analysis
   - Financial ratios
   - Quarterly earnings
   - Revenue growth
   - P/E ratio analysis

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Unix/macOS
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```
NEWS_API_KEY=your_news_api_key
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_secret
BROKER_API_KEY=your_broker_api_key
BROKER_API_SECRET=your_broker_secret
```

4. Run the application:
```bash
python app.py
```

## Features

- Real-time stock data from NSE/BSE
- Sentiment analysis from social media and news
- Technical analysis with multiple indicators
- Fundamental analysis of companies
- Automated trading recommendations
- One-click trade execution
- Interactive charts and visualizations

## Code Quality

This project uses SonarQube for continuous code quality inspection. SonarQube analyzes:
- Code quality
- Test coverage
- Code duplication
- Security vulnerabilities
- Technical debt

### SonarQube Setup

1. Set up SonarQube server:
   - Self-hosted: Follow [SonarQube installation guide](https://docs.sonarqube.org/latest/setup/install-server/)
   - Cloud: Use [SonarCloud](https://sonarcloud.io)

2. Configure GitHub secrets:
   ```
   SONAR_TOKEN=your-sonar-token
   SONAR_HOST_URL=your-sonar-url
   ```

3. Quality Gates:
   - Code coverage: minimum 80%
   - Duplicated lines: maximum 3%
   - Technical debt ratio: maximum 5%
   - Security vulnerabilities: 0 critical issues

## Note
Please ensure you have the necessary API keys and trading account credentials before using the trading features.
