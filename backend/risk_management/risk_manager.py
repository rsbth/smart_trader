import logging

logger = logging.getLogger(__name__)

class RiskManager:
    def __init__(self):
        self.max_position_size = 100000  # Maximum position size in currency
        self.max_loss_percent = 0.02     # Maximum loss per trade (2%)
        self.max_portfolio_risk = 0.05   # Maximum portfolio risk (5%)
        self.position_sizing_factor = 0.01  # Position sizing factor (1%)

    def calculate_position_size(self, price, stop_loss):
        """Calculate the position size based on risk parameters"""
        try:
            if not price or not stop_loss:
                return 0
            
            risk_per_share = abs(price - stop_loss)
            if risk_per_share == 0:
                return 0
            
            max_shares = self.max_position_size / price
            risk_based_shares = (self.max_position_size * self.position_sizing_factor) / risk_per_share
            
            return min(max_shares, risk_based_shares)
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return 0

    def validate_trade(self, symbol, quantity, price, stop_loss):
        """Validate if a trade meets risk management criteria"""
        try:
            # Check if position size is within limits
            position_value = quantity * price
            if position_value > self.max_position_size:
                return False, "Position size exceeds maximum limit"
            
            # Check stop loss percentage
            if stop_loss:
                loss_percent = abs(price - stop_loss) / price
                if loss_percent > self.max_loss_percent:
                    return False, "Stop loss exceeds maximum allowed loss percentage"
            
            return True, "Trade meets risk management criteria"
        except Exception as e:
            logger.error(f"Error validating trade: {str(e)}")
            return False, f"Error validating trade: {str(e)}"

    def adjust_position_size(self, portfolio_value, proposed_position_value):
        """Adjust position size based on portfolio risk"""
        try:
            max_position_value = portfolio_value * self.max_portfolio_risk
            if proposed_position_value > max_position_value:
                return max_position_value
            return proposed_position_value
        except Exception as e:
            logger.error(f"Error adjusting position size: {str(e)}")
            return 0

# Create a risk manager instance
risk_manager = RiskManager()
