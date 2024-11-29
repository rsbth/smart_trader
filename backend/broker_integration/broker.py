from kiteconnect import KiteConnect
from flask import current_app
import os
from dotenv import load_dotenv

load_dotenv()

class ZerodhaBroker:
    def __init__(self):
        self.api_key = os.getenv('BROKER_API_KEY')
        self.api_secret = os.getenv('BROKER_API_SECRET')
        self.redirect_url = "http://127.0.0.1:5000/api/v1/broker/callback"
        self.kite = KiteConnect(api_key=self.api_key)
        self.access_token = None

    def get_login_url(self):
        """Generate the login URL for Zerodha authentication"""
        return self.kite.login_url()

    def set_access_token(self, request_token):
        """Generate and set access token from request token"""
        try:
            data = self.kite.generate_session(request_token, api_secret=self.api_secret)
            self.access_token = data["access_token"]
            self.kite.set_access_token(self.access_token)
            return True
        except Exception as e:
            current_app.logger.error(f"Error setting access token: {str(e)}")
            return False

    def get_holdings(self):
        """Get user's holdings"""
        try:
            return self.kite.holdings()
        except Exception as e:
            current_app.logger.error(f"Error fetching holdings: {str(e)}")
            return None

    def get_positions(self):
        """Get user's positions"""
        try:
            return self.kite.positions()
        except Exception as e:
            current_app.logger.error(f"Error fetching positions: {str(e)}")
            return None

    def execute_trade(self, symbol, transaction_type, quantity, price=None):
        """Execute a trade"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated with Zerodha")

            order_type = "MARKET" if price is None else "LIMIT"
            
            order_id = self.kite.place_order(
                variety=self.kite.VARIETY_REGULAR,
                exchange=self.kite.EXCHANGE_NSE,
                tradingsymbol=symbol,
                transaction_type=transaction_type,
                quantity=quantity,
                product=self.kite.PRODUCT_CNC,
                order_type=order_type,
                price=price
            )
            return {"status": "success", "order_id": order_id}
        except Exception as e:
            current_app.logger.error(f"Error executing trade: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_order_status(self, order_id):
        """Get status of an order"""
        try:
            orders = self.kite.orders()
            for order in orders:
                if order['order_id'] == order_id:
                    return order['status']
            return None
        except Exception as e:
            current_app.logger.error(f"Error fetching order status: {str(e)}")
            return None

# Create a broker instance
broker = ZerodhaBroker()
