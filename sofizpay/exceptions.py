"""Custom exceptions for SofizPay SDK"""


class SofizPayError(Exception):
    """Base exception for all SofizPay SDK errors"""
    pass


class PaymentError(SofizPayError):
    """Exception raised for payment-related errors"""
    pass


class TransactionError(SofizPayError):
    """Exception raised for transaction-related errors"""
    pass


class NetworkError(SofizPayError):
    """Exception raised for network-related errors"""
    pass


class ValidationError(SofizPayError):
    """Exception raised for validation errors"""
    pass


class RateLimitError(NetworkError):
    """Exception raised when API rate limit is exceeded"""
    pass


class InsufficientBalanceError(PaymentError):
    """Exception raised when account has insufficient balance"""
    pass


class InvalidAccountError(ValidationError):
    """Exception raised when account is invalid"""
    pass


class InvalidAssetError(ValidationError):
    """Exception raised when asset is invalid"""
    pass
