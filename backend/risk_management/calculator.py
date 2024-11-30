import logging

logger = logging.getLogger(__name__)

class RiskCalculator:
    def __init__(self):
        self.max_position_size = 100000  # Maximum position size in currency
        self.max_loss_percent = 0.02     # Maximum loss per trade (2%)
        self.max_portfolio_risk = 0.05   # Maximum portfolio risk (5%)
        self.position_sizing_factor = 0.01  # Position sizing factor (1%)

    def calculate_position_size(self, price, stop_loss, portfolio_value):
        """Calculate the position size based on risk parameters"""
        try:
            if not price or not stop_loss or not portfolio_value:
                return 0
            
            # Calculate risk per share
            risk_per_share = abs(price - stop_loss)
            if risk_per_share == 0:
                return 0
            
            # Calculate maximum risk amount based on portfolio value
            max_risk_amount = portfolio_value * self.max_loss_percent
            
            # Calculate number of shares based on risk
            shares = max_risk_amount / risk_per_share
            
            # Calculate position value
            position_value = shares * price
            
            # Check against maximum position size
            if position_value > self.max_position_size:
                shares = self.max_position_size / price
            
            # Check against portfolio risk
            max_position_value = portfolio_value * self.max_portfolio_risk
            if position_value > max_position_value:
                shares = max_position_value / price
            
            return int(shares)  # Round down to nearest whole share
        except Exception as e:
            logger.error(f"Error calculating position size: {str(e)}")
            return 0

    def calculate_risk_reward_ratio(self, entry_price, stop_loss, target_price):
        """Calculate risk-reward ratio for a trade"""
        try:
            if not entry_price or not stop_loss or not target_price:
                return 0
            
            risk = abs(entry_price - stop_loss)
            reward = abs(target_price - entry_price)
            
            if risk == 0:
                return 0
            
            return reward / risk
        except Exception as e:
            logger.error(f"Error calculating risk-reward ratio: {str(e)}")
            return 0

    def calculate_portfolio_risk(self, positions, portfolio_value):
        """Calculate total portfolio risk"""
        try:
            if not positions or not portfolio_value:
                return 0
            
            total_risk = sum(
                abs(pos['current_price'] - pos['stop_loss']) * pos['quantity']
                for pos in positions
                if 'stop_loss' in pos
            )
            
            return total_risk / portfolio_value
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {str(e)}")
            return 0

    def validate_trade(self, price, quantity, stop_loss, portfolio_value, existing_positions=None):
        """Validate if a trade meets risk management criteria"""
        try:
            # Check basic parameters
            if not all([price, quantity, stop_loss, portfolio_value]):
                return False, "Missing required parameters"
            
            # Calculate position value
            position_value = price * quantity
            
            # Check maximum position size
            if position_value > self.max_position_size:
                return False, "Position size exceeds maximum limit"
            
            # Calculate trade risk
            risk_per_share = abs(price - stop_loss)
            total_risk = risk_per_share * quantity
            risk_percent = total_risk / portfolio_value
            
            # Check trade risk
            if risk_percent > self.max_loss_percent:
                return False, "Trade risk exceeds maximum allowed loss percentage"
            
            # Check portfolio risk if we have existing positions
            if existing_positions:
                current_portfolio_risk = self.calculate_portfolio_risk(existing_positions, portfolio_value)
                new_portfolio_risk = current_portfolio_risk + risk_percent
                
                if new_portfolio_risk > self.max_portfolio_risk:
                    return False, "Total portfolio risk would exceed maximum limit"
            
            return True, "Trade meets risk management criteria"
        except Exception as e:
            logger.error(f"Error validating trade: {str(e)}")
            return False, f"Error validating trade: {str(e)}"

# Create a risk calculator instance
risk_calculator = RiskCalculator()
