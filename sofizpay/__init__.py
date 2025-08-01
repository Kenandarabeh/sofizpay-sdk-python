"""
SofizPay SDK - Python library for Stellar-based payments

This SDK provides easy-to-use functions for integrating SofizPay 
payment functionality into Python applications.
"""

from .client import SofizPayClient
from .payments import PaymentManager
from .transactions import TransactionManager
from .exceptions import (
    SofizPayError,
    PaymentError,
    TransactionError,
    NetworkError,
    ValidationError
)

__version__ = "1.0.2"
__author__ = "SofizPay Team"
__email__ = "support@sofizpay.com"

__all__ = [
    "SofizPayClient",
    "PaymentManager", 
    "TransactionManager",
    "SofizPayError",
    "PaymentError",
    "TransactionError",
    "NetworkError",
    "ValidationError"
]

# Convenience functions for easy access
def make_cib_transaction(transaction_data):
    """Convenience function to make CIB transaction"""
    client = SofizPayClient()
    return client.make_cib_transaction(transaction_data)

def verify_sofizpay_signature(verification_data):
    """Convenience function to verify SofizPay signature"""
    client = SofizPayClient()
    return client.verify_sofizpay_signature(verification_data)
