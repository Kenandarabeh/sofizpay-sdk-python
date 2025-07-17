"""Utility functions for SofizPay SDK"""

import asyncio
import time
from typing import Callable, Any, Optional
from stellar_sdk import Keypair
from .exceptions import ValidationError, NetworkError
import requests


async def sleep(ms: int) -> None:
    """Sleep for the specified number of milliseconds"""
    await asyncio.sleep(ms / 1000)


async def fetch_with_retry(
    url: str, 
    retries: int = 3, 
    delay: int = 1000,
    session: Optional[requests.Session] = None
) -> dict:
    """
    Fetch data from URL with retry logic for rate limiting
    
    Args:
        url: The URL to fetch
        retries: Number of retry attempts
        delay: Delay between retries in milliseconds
        session: Optional requests session to use
        
    Returns:
        Response data as dictionary
        
    Raises:
        NetworkError: When all retries are exhausted
    """
    if session is None:
        session = requests.Session()
    
    for i in range(retries):
        try:
            response = session.get(url)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and i < retries - 1:
                await sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                raise NetworkError(f"HTTP error: {e}")
        except requests.exceptions.RequestException as e:
            if i < retries - 1:
                await sleep(delay)
                delay *= 2
            else:
                raise NetworkError(f"Request error: {e}")
    
    raise NetworkError(f"Failed to fetch {url} after {retries} retries")


def validate_public_key(public_key: str) -> bool:
    """
    Validate Stellar public key format
    
    Args:
        public_key: The public key to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        Keypair.from_public_key(public_key)
        return True
    except Exception:
        return False


def validate_secret_key(secret_key: str) -> bool:
    """
    Validate Stellar secret key format
    
    Args:
        secret_key: The secret key to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        Keypair.from_secret(secret_key)
        return True
    except Exception:
        return False


def get_public_key_from_secret(secret_key: str) -> str:
    """
    Extract public key from secret key
    
    Args:
        secret_key: The secret key
        
    Returns:
        The corresponding public key
        
    Raises:
        ValidationError: If secret key is invalid
    """
    try:
        keypair = Keypair.from_secret(secret_key)
        return keypair.public_key
    except Exception as e:
        raise ValidationError(f"Invalid secret key: {e}")


def validate_amount(amount: str) -> bool:
    """
    Validate payment amount
    
    Args:
        amount: The amount to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        amount_float = float(amount)
        return amount_float > 0 and amount_float <= 922337203685.4775807
    except (ValueError, TypeError):
        return False


def validate_memo(memo: str) -> tuple[bool, str]:
    """
    Validate and optionally truncate memo
    
    Args:
        memo: The memo to validate
        
    Returns:
        Tuple of (is_valid, processed_memo)
    """
    if memo is None:
        return True, ""
    
    if len(memo) > 28:
        truncated_memo = memo[:28]
        return True, truncated_memo
    
    return True, memo


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int = 10, time_window: int = 1):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    async def acquire(self):
        """Acquire a rate limit slot, blocking if necessary"""
        now = time.time()
        
        # Remove old calls outside the time window
        self.calls = [call_time for call_time in self.calls if now - call_time < self.time_window]
        
        if len(self.calls) >= self.max_calls:
            # Wait until we can make another call
            oldest_call = min(self.calls)
            wait_time = self.time_window - (now - oldest_call)
            if wait_time > 0:
                await asyncio.sleep(wait_time)
        
        self.calls.append(now)
