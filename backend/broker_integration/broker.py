from smartapi import SmartConnect
from flask import current_app
import os
from dotenv import load_dotenv
import pyotp

load_dotenv()

class AngelBroker:
    def __init__(self):
        self.api_key = os.getenv('ANGEL_API_KEY')
        self.client_id = os.getenv('ANGEL_CLIENT_ID')
        self.pin = os.getenv('ANGEL_PIN')
        self.totp_key = os.getenv('ANGEL_TOTP_KEY')
        self.smart_api = SmartConnect(api_key=self.api_key)
        self.access_token = None
        self.refresh_token = None
        self.feed_token = None

    def login(self):
        """Login to Angel Broking"""
        try:
            totp = pyotp.TOTP(self.totp_key)
            data = self.smart_api.generateSession(
                self.client_id,
                self.pin,
                totp.now()
            )
            self.refresh_token = data['data']['refreshToken']
            self.access_token = data['data']['jwtToken']
            self.feed_token = self.smart_api.getfeedToken()
            return True
        except Exception as e:
            current_app.logger.error(f"Error logging in: {str(e)}")
            return False

    def get_profile(self):
        """Get user profile"""
        try:
            return self.smart_api.getProfile()
        except Exception as e:
            current_app.logger.error(f"Error fetching profile: {str(e)}")
            return None

    def get_holdings(self):
        """Get user's holdings"""
        try:
            return self.smart_api.holding()
        except Exception as e:
            current_app.logger.error(f"Error fetching holdings: {str(e)}")
            return None

    def get_positions(self):
        """Get user's positions"""
        try:
            return self.smart_api.position()
        except Exception as e:
            current_app.logger.error(f"Error fetching positions: {str(e)}")
            return None

    def execute_trade(self, symbol, transaction_type, quantity, price=None):
        """Execute a trade"""
        try:
            if not self.access_token:
                raise Exception("Not authenticated with Angel Broking")

            # Prepare order parameters
            order_params = {
                "variety": "NORMAL",
                "tradingsymbol": symbol,
                "symboltoken": self._get_token(symbol),
                "transactiontype": transaction_type,  # "BUY" or "SELL"
                "exchange": "NSE",
                "ordertype": "MARKET" if price is None else "LIMIT",
                "producttype": "DELIVERY",
                "duration": "DAY",
                "quantity": quantity
            }

            if price:
                order_params["price"] = price

            # Place order
            order_id = self.smart_api.placeOrder(order_params)
            return {"status": "success", "order_id": order_id}
        except Exception as e:
            current_app.logger.error(f"Error executing trade: {str(e)}")
            return {"status": "error", "message": str(e)}

    def get_order_status(self, order_id):
        """Get status of an order"""
        try:
            orders = self.smart_api.orderBook()
            for order in orders['data']:
                if order['orderid'] == order_id:
                    return order['status']
            return None
        except Exception as e:
            current_app.logger.error(f"Error fetching order status: {str(e)}")
            return None

    def get_order_book(self):
        """Get complete order book"""
        try:
            return self.smart_api.orderBook()['data']
        except Exception as e:
            current_app.logger.error(f"Error fetching order book: {str(e)}")
            return None

    def cancel_order(self, order_id):
        """Cancel an order"""
        try:
            return self.smart_api.cancelOrder(order_id, variety="NORMAL")
        except Exception as e:
            current_app.logger.error(f"Error cancelling order: {str(e)}")
            return None

    def get_funds(self):
        """Get fund details"""
        try:
            return self.smart_api.rmsLimit()['data']
        except Exception as e:
            current_app.logger.error(f"Error fetching funds: {str(e)}")
            return None

    def _get_token(self, symbol):
        """Get token for a symbol"""
        try:
            # You might want to maintain a cache of symbols and their tokens
            # For now, we'll need to implement this based on your needs
            # You can use self.smart_api.searchScrip() or maintain a mapping
            pass
        except Exception as e:
            current_app.logger.error(f"Error getting token for symbol {symbol}: {str(e)}")
            return None

# Create a broker instance
broker = AngelBroker()
