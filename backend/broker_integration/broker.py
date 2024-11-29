from kiteconnect import KiteConnect
import os
from datetime import datetime

class BrokerInterface:
    def __init__(self):
        self.api_key = os.getenv('BROKER_API_KEY')
        self.api_secret = os.getenv('BROKER_API_SECRET')
        self.kite = KiteConnect(api_key=self.api_key)
        
        # Initialize connection
        self._initialize_connection()
    
    def _initialize_connection(self):
        if not hasattr(self, 'access_token'):
            # In production, implement proper OAuth flow
            # For now, we'll assume access token is stored in env
            self.access_token = os.getenv('BROKER_ACCESS_TOKEN')
            if self.access_token:
                self.kite.set_access_token(self.access_token)
    
    def execute_trade(self, symbol, transaction_type, quantity, price=None):
        try:
            # Ensure connection is initialized
            self._initialize_connection()
            
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
        try:
            return self.kite.positions()
        except Exception as e:
            return {'error': str(e)}
    
    def get_holdings(self):
        try:
            return self.kite.holdings()
        except Exception as e:
            return {'error': str(e)}
    
    def get_order_history(self, order_id=None):
        try:
            if order_id:
                return self.kite.order_history(order_id)
            return self.kite.orders()
        except Exception as e:
            return {'error': str(e)}
    
    def get_margins(self):
        try:
            return self.kite.margins()
        except Exception as e:
            return {'error': str(e)}
    
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
            return {'error': str(e)}
    
    def cancel_order(self, order_id):
        try:
            return self.kite.cancel_order(
                variety="regular",
                order_id=order_id
            )
        except Exception as e:
            return {'error': str(e)}
