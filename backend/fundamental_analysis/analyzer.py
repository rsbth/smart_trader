import yfinance as yf
from bs4 import BeautifulSoup
import requests

class FundamentalAnalyzer:
    def __init__(self):
        pass
    
    def analyze(self, symbol):
        # Get stock information
        stock = yf.Ticker(symbol)
        
        try:
            # Get financial metrics
            info = stock.info
            
            # Get quarterly financials
            quarterly_financials = stock.quarterly_financials
            
            # Calculate key metrics
            metrics = self._calculate_metrics(info, quarterly_financials)
            
            return metrics
        
        except Exception as e:
            print(f"Error analyzing fundamentals: {str(e)}")
            return None
    
    def _calculate_metrics(self, info, quarterly_financials):
        metrics = {}
        
        # Basic metrics
        metrics['market_cap'] = info.get('marketCap')
        metrics['pe_ratio'] = info.get('trailingPE')
        metrics['forward_pe'] = info.get('forwardPE')
        metrics['price_to_book'] = info.get('priceToBook')
        
        # Revenue metrics
        if not quarterly_financials.empty:
            total_revenue = quarterly_financials.loc['Total Revenue']
            metrics['quarterly_revenue'] = total_revenue.iloc[0]  # Most recent quarter
            
            # Calculate revenue growth
            if len(total_revenue) >= 2:
                revenue_growth = ((total_revenue.iloc[0] - total_revenue.iloc[-1]) 
                                / total_revenue.iloc[-1] * 100)
                metrics['revenue_growth'] = revenue_growth
        
        # Profitability metrics
        metrics['profit_margins'] = info.get('profitMargins')
        metrics['operating_margins'] = info.get('operatingMargins')
        
        # Dividend metrics
        metrics['dividend_yield'] = info.get('dividendYield')
        metrics['payout_ratio'] = info.get('payoutRatio')
        
        # Debt metrics
        metrics['debt_to_equity'] = info.get('debtToEquity')
        metrics['current_ratio'] = info.get('currentRatio')
        
        # Growth metrics
        metrics['earnings_growth'] = info.get('earningsGrowth')
        metrics['revenue_growth_yearly'] = info.get('revenueGrowth')
        
        # Remove None values
        metrics = {k: v for k, v in metrics.items() if v is not None}
        
        return metrics
    
    def _get_quarterly_earnings(self, symbol):
        try:
            url = f"https://finance.yahoo.com/quote/{symbol}/analysis"
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            earnings_table = soup.find('table', {'class': 'W(100%) M(0) BdB Bdc($seperatorColor)'})
            if earnings_table:
                rows = earnings_table.find_all('tr')
                earnings_data = []
                
                for row in rows[1:]:  # Skip header row
                    cols = row.find_all('td')
                    if cols:
                        quarter = cols[0].text.strip()
                        eps_estimate = cols[1].text.strip()
                        eps_actual = cols[2].text.strip()
                        surprise = cols[3].text.strip()
                        
                        earnings_data.append({
                            'quarter': quarter,
                            'eps_estimate': eps_estimate,
                            'eps_actual': eps_actual,
                            'surprise': surprise
                        })
                
                return earnings_data
            
            return None
        
        except Exception as e:
            print(f"Error fetching quarterly earnings: {str(e)}")
            return None
