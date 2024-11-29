from kiteconnect import KiteConnect
from flask import current_app, redirect, request, session, url_for
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

class BrokerInterface:
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

    def execute_trade(self, symbol, transaction_type, quantity, price=None):
        try:
            # Ensure connection is initialized
            if not self.access_token:
                raise Exception("Access token not set")

            # Prepare order parameters
            order_params = {
                "tradingsymbol": symbol,
                "exchange": "NSE",  # or "BSE"
                "transaction_type": transaction_type,  # "BUY" or "SELL"
                "quantity": quantity,
                "product": "CNC",  # CNC for delivery, MIS for intraday
                "order_type": "MARKET" if price is None else "LIMIT",
            }
            
            if price:
                order_params["price"] = price
            
            # Place order
            order_id = self.kite.place_order(
                variety="regular",
                **order_params
            )
            
            # Get order status
            order_status = self.kite.order_history(order_id)[-1]
            
            return {
                'status': 'success',
                'order_id': order_id,
                'order_status': order_status['status'],
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def get_positions(self):
        """Get user's positions"""
        try:
            return self.kite.positions()
        except Exception as e:
            current_app.logger.error(f"Error fetching positions: {str(e)}")
            return None

    def get_holdings(self):
        """Get user's holdings"""
        try:
            return self.kite.holdings()
        except Exception as e:
            current_app.logger.error(f"Error fetching holdings: {str(e)}")
            return None

    def get_order_history(self, order_id=None):
        try:
            if order_id:
                return self.kite.order_history(order_id)
            return self.kite.orders()
        except Exception as e:
            current_app.logger.error(f"Error fetching order history: {str(e)}")
            return None

    def get_margins(self):
        try:
            return self.kite.margins()
        except Exception as e:
            current_app.logger.error(f"Error fetching margins: {str(e)}")
            return None

    def modify_order(self, order_id, price=None, quantity=None, order_type=None):
        try:
            params = {}
            if price:
                params['price'] = price
            if quantity:
                params['quantity'] = quantity
            if order_type:
                params['order_type'] = order_type
            
            return self.kite.modify_order(
                variety="regular",
                order_id=order_id,
                **params
            )
        except Exception as e:
            current_app.logger.error(f"Error modifying order: {str(e)}")
            return None

    def cancel_order(self, order_id):
        try:
            return self.kite.cancel_order(
                variety="regular",
                order_id=order_id
            )
        except Exception as e:
            current_app.logger.error(f"Error cancelling order: {str(e)}")
            return None
