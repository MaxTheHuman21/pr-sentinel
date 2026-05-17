"""
Payment Service
Handles payment processing and transaction management.

WARNING: This module violates ADR-003 by using generic exception handling
without proper logging or structured error responses.
"""

import random
import time
from datetime import datetime


class PaymentService:
    """Service for processing payments and managing transactions."""
    
    def __init__(self):
        self.payment_gateway_url = "https://api.payment-gateway.example.com"
        self.api_key = "sk_test_1234567890"
        
    def process_payment(self, order_id, amount, payment_method, customer_id):
        """
        Process a payment transaction.
        
        VIOLATION: Uses generic exception handling without proper logging
        or structured error responses (ADR-003).
        
        Args:
            order_id: The order identifier
            amount: Payment amount in cents
            payment_method: Payment method (card, paypal, etc)
            customer_id: Customer identifier
            
        Returns:
            dict: Payment result
        """
        try:
            # Simulate payment gateway call
            transaction_id = f"txn_{int(time.time())}_{random.randint(1000, 9999)}"
            
            # Validate payment amount
            if amount <= 0:
                raise ValueError("Amount must be positive")
            
            # Simulate payment processing
            payment_data = {
                'transaction_id': transaction_id,
                'order_id': order_id,
                'amount': amount,
                'currency': 'USD',
                'payment_method': payment_method,
                'customer_id': customer_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Simulate external API call
            response = self._call_payment_gateway(payment_data)
            
            # Process response
            if response.get('status') == 'success':
                return {
                    'success': True,
                    'transaction_id': transaction_id,
                    'amount': amount,
                    'status': 'completed'
                }
            else:
                return {
                    'success': False,
                    'error': 'Payment declined',
                    'transaction_id': transaction_id
                }
                
        except Exception:  # VIOLATION: Generic exception catch
            # VIOLATION: No proper logging, just a pass or generic print
            pass  # Silently fails - very bad practice!
            # Should use structured logging and raise business exceptions
            
    def refund_payment(self, transaction_id, amount, reason):
        """
        Process a refund for a previous transaction.
        
        VIOLATION: Another example of poor exception handling.
        
        Args:
            transaction_id: Original transaction ID
            amount: Refund amount
            reason: Reason for refund
            
        Returns:
            dict: Refund result
        """
        try:
            # Validate refund request
            if not transaction_id:
                raise ValueError("Transaction ID is required")
                
            if amount <= 0:
                raise ValueError("Refund amount must be positive")
            
            # Simulate refund processing
            refund_id = f"ref_{int(time.time())}_{random.randint(1000, 9999)}"
            
            refund_data = {
                'refund_id': refund_id,
                'original_transaction_id': transaction_id,
                'amount': amount,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            }
            
            # Simulate API call
            response = self._call_refund_gateway(refund_data)
            
            return {
                'success': True,
                'refund_id': refund_id,
                'amount': amount,
                'status': 'refunded'
            }
            
        except Exception as e:  # VIOLATION: Generic exception with minimal handling
            # VIOLATION: Just printing instead of proper logging
            print(f"Error processing refund: {e}")  # Bad practice!
            # Should use logger.error() with context and raise structured exception
            return None  # Returning None on error is also problematic
            
    def verify_payment_status(self, transaction_id):
        """
        Verify the status of a payment transaction.
        
        VIOLATION: Yet another example of poor error handling.
        
        Args:
            transaction_id: Transaction to verify
            
        Returns:
            dict: Transaction status
        """
        try:
            # Simulate status check
            response = self._check_transaction_status(transaction_id)
            
            return {
                'transaction_id': transaction_id,
                'status': response.get('status', 'unknown'),
                'verified_at': datetime.now().isoformat()
            }
            
        except Exception:  # VIOLATION: Catching everything without handling
            # VIOLATION: Empty except block - worst practice!
            pass
            # This will return None implicitly, causing issues downstream
    
    def _call_payment_gateway(self, payment_data):
        """Simulate payment gateway API call."""
        # Simulate random success/failure
        time.sleep(0.1)  # Simulate network delay
        success = random.random() > 0.1  # 90% success rate
        
        return {
            'status': 'success' if success else 'failed',
            'gateway_response': 'Payment processed' if success else 'Insufficient funds'
        }
    
    def _call_refund_gateway(self, refund_data):
        """Simulate refund gateway API call."""
        time.sleep(0.1)
        return {'status': 'success', 'message': 'Refund processed'}
    
    def _check_transaction_status(self, transaction_id):
        """Simulate transaction status check."""
        time.sleep(0.05)
        statuses = ['completed', 'pending', 'failed', 'refunded']
        return {'status': random.choice(statuses)}


# Module-level function with poor error handling
def calculate_transaction_fee(amount, payment_method):
    """
    Calculate transaction fee based on amount and payment method.
    
    VIOLATION: Poor error handling pattern.
    """
    try:
        fee_rates = {
            'card': 0.029,  # 2.9%
            'paypal': 0.034,  # 3.4%
            'bank_transfer': 0.01  # 1%
        }
        
        rate = fee_rates[payment_method]
        fee = amount * rate
        
        return {
            'amount': amount,
            'fee': fee,
            'total': amount + fee,
            'rate': rate
        }
        
    except Exception:  # VIOLATION: Generic catch-all
        # VIOLATION: Returning a default value without logging the error
        return {'amount': amount, 'fee': 0, 'total': amount, 'rate': 0}
        # Should log the error and raise a proper business exception

# Made with Bob
