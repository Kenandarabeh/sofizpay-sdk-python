# SofizPay SDK for Python

<div align="center">
  <img src="https://github.com/kenandarabeh/sofizpay-sdk-python/blob/main/assets/sofizpay-logo.png?raw=true" alt="SofizPay Logo" width="200" height="200">
  
  <h3>🚀 A powerful Python SDK for Stellar blockchain payments</h3>
  
  [![PyPI Version](https://img.shields.io/pypi/v/sofizpay-sdk-python.svg)](https://pypi.org/project/sofizpay-sdk-python/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![GitHub Stars](https://img.shields.io/github/stars/sofizpay/sofizpay-sdk-python.svg)](https://github.com/sofizpay/sofizpay-sdk-python/stargazers)
  [![Issues](https://img.shields.io/github/issues/sofizpay/sofizpay-sdk-python.svg)](https://github.com/sofizpay/sofizpay-sdk-python/issues)
  [![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [API Reference](#api-reference)
- [Usage Examples](#usage-examples)
- [Real-time Transaction Monitoring](#real-time-transaction-monitoring)
- [CIB Transactions](#cib-transactions)
- [Signature Verification](#signature-verification)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)
- [Contributing](#contributing)
- [Support](#support)
- [License](#license)

---

## 🌟 Overview

SofizPay SDK is a powerful Python library for Stellar blockchain payments with real-time transaction monitoring, comprehensive payment management, and signature verification capabilities.

**Key Benefits:**
- 🔐 Secure Stellar blockchain integration
- ⚡ Real-time transaction monitoring with async support
- 🎯 Simple, intuitive API with type hints
- 📱 Cross-platform Python support (3.8+)
- 🔒 Built-in signature verification
- 🏦 CIB transaction support

---

## ✨ Features

- ✅ **Send Payments**: Secure token transfers with memo support
- ✅ **Transaction History**: Retrieve and filter transaction records  
- ✅ **Balance Checking**: Real-time balance queries
- ✅ **Transaction Search**: Find transactions by hash with detailed info
- ✅ **Real-time Streams**: Live transaction monitoring with async callbacks
- ✅ **CIB Transactions**: Create CIB bank transactions for deposits
- ✅ **Signature Verification**: Verify SofizPay signatures and custom signatures
- ✅ **Error Handling**: Robust async error management and reporting
- ✅ **Rate Limiting**: Built-in API rate limiting protection
- ✅ **Type Safety**: Full type hints for better development experience

---

## 📦 Installation

Install SofizPay SDK using pip:

```bash
pip install sofizpay-sdk-python
```

For development with all dependencies:

```bash
pip install sofizpay-sdk-python[dev]
```

### Requirements

- Python 3.8+
- stellar-sdk
- cryptography
- requests

---

## 🚀 Quick Start

### 1. Import the SDK

```python
import asyncio
from sofizpay import SofizPayClient
```

### 2. Initialize the Client

```python
# Initialize with default Stellar mainnet
client = SofizPayClient()
```

### 3. Your First Payment

```python
async def send_payment():
    client = SofizPayClient()
    
    result = await client.send_payment(
        source_secret="YOUR_SECRET_KEY",
        destination_public_key="DESTINATION_PUBLIC_KEY",
        amount="10.50",
        memo="Payment for services"
    )
    
    if result["success"]:
        print(f'Payment successful! TX: {result["hash"]}')
    else:
        print(f'Payment failed: {result["error"]}')

# Run the async function
asyncio.run(send_payment())
```

---

## 📚 API Reference

### Core Payment Operations

#### `send_payment()` - Send Payment
```python
result = await client.send_payment(
    source_secret="SECRET_KEY",
    destination_public_key="DESTINATION_PUBLIC_KEY", 
    amount="10.50",
    memo="Payment memo"  # Optional
)
```

#### `get_balance()` - Check Balance
```python
balance = await client.get_dzt_balance("PUBLIC_KEY")
print(f'Balance: {balance}')
```

#### `get_all_transactions()` - Get Transactions
```python
transactions = await client.get_all_transactions("PUBLIC_KEY", limit=50)
for tx in transactions:
    print(f'TX: {tx["hash"]} - Amount: {tx["amount"]}')
```

### Transaction Monitoring

#### `setup_transaction_stream()` - Real-time Monitoring
```python
def handle_transaction(transaction):
    print(f'New {transaction["type"]}: {transaction["amount"]}')

stream_id = await client.setup_transaction_stream("PUBLIC_KEY", handle_transaction)
```

#### `stop_transaction_stream()` - Stop Monitoring
```python
success = client.stop_transaction_stream(stream_id)
```

#### `get_transaction_by_hash()` - Get Transaction Details
```python
result = await client.get_transaction_by_hash("TRANSACTION_HASH")
if result["found"]:
    tx = result["transaction"]
    print(f'Amount: {tx["amount"]}')
```

### CIB Transactions

#### `make_cib_transaction()` - Create CIB Transaction
```python
result = await client.make_cib_transaction({
    "account": "ACCOUNT_NUMBER",
    "amount": 100.50,
    "full_name": "John Doe",
    "phone": "+1234567890",
    "email": "john@example.com",
    "memo": "Payment for order",
    "return_url": "https://your-site.com/callback"
})
```

### Signature Verification

#### `verify_signature()` - Verify Custom Signature
```python
is_valid = client.verify_signature(
    message="Hello, world!",
    signature="BASE64_SIGNATURE",
)
```

#### `verify_sofizpay_signature()` - Verify SofizPay Signature
```python
is_valid = client.verify_sofizpay_signature({
    "message": "wc_order_123success",
    "signature_url_safe": "URL_SAFE_BASE64_SIGNATURE"
})
```

### Utility Methods

#### `get_public_key_from_secret()` - Extract Public Key
```python
public_key = client.get_public_key_from_secret("SECRET_KEY")
```

---

## 🔄 Real-time Transaction Monitoring

### Basic Monitoring Setup

```python
import asyncio
from sofizpay import SofizPayClient

async def monitor_transactions():
    client = SofizPayClient()
    
    def transaction_handler(transaction):
        print(f'🎉 NEW TRANSACTION!')
        print(f'   Type: {transaction["type"]}')
        print(f'   Amount: {transaction["amount"]}')
        print(f'   From: {transaction["from"]}')
        print(f'   To: {transaction["to"]}')
        print(f'   Memo: {transaction["memo"]}')
        print(f'   Time: {transaction["created_at"]}')
        
        # Process the transaction
        if transaction["type"] == "received":
            handle_incoming_payment(transaction)
    
    # Start monitoring (only NEW transactions after this point)
    stream_id = await client.setup_transaction_stream(
        "YOUR_PUBLIC_KEY", 
        transaction_handler
    )
    
    print(f"📡 Monitoring started with stream ID: {stream_id}")
    
    # Keep monitoring for 60 seconds
    await asyncio.sleep(60)
    
    # Stop monitoring
    stopped = client.stop_transaction_stream(stream_id)
    print(f"🛑 Monitoring stopped: {stopped}")

def handle_incoming_payment(transaction):
    """Process incoming payments"""
    amount = float(transaction["amount"])
    if amount >= 10.0:
        print(f"✅ Large payment received: {amount}")
        # Process large payment...
    else:
        print(f"💰 Small payment received: {amount}")

# Run monitoring
asyncio.run(monitor_transactions())
```

### Advanced Monitoring with Error Handling

```python
class PaymentMonitor:
    def __init__(self):
        self.client = SofizPayClient()
        self.active_streams = {}
    
    async def start_monitoring(self, public_key: str):
        """Start monitoring with error handling"""
        try:
            stream_id = await self.client.setup_transaction_stream(
                public_key, 
                self._handle_transaction
            )
            self.active_streams[public_key] = stream_id
            print(f"✅ Started monitoring for {public_key}")
            return stream_id
        except Exception as e:
            print(f"❌ Failed to start monitoring: {e}")
            return None
    
    def _handle_transaction(self, transaction):
        """Handle incoming transactions"""
        try:
            print(f"📩 New transaction: {transaction['amount']}")
            # Your business logic here
        except Exception as e:
            print(f"❌ Error processing transaction: {e}")
    
    def stop_monitoring(self, public_key: str):
        """Stop monitoring for a specific key"""
        if public_key in self.active_streams:
            stream_id = self.active_streams[public_key]
            success = self.client.stop_transaction_stream(stream_id)
            del self.active_streams[public_key]
            return success
        return False
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # Stop all active streams
        for public_key in list(self.active_streams.keys()):
            self.stop_monitoring(public_key)
```

---

## 🏦 CIB Transactions

### Basic CIB Transaction

```python
async def create_cib_transaction():
    client = SofizPayClient()
    
    transaction_data = {
        "account": "DZ1234567890123456789012",
        "amount": 150.75,
        "full_name": "Ahmed Mohammed",
        "phone": "+213555123456",
        "email": "ahmed@example.com",
        "memo": "Payment for order #12345",
        "return_url": "https://mystore.com/payment/success"
    }
    
    try:
        result = await client.make_cib_transaction(transaction_data)
        
        if result["success"]:
            print("✅ CIB Transaction created successfully!")
            print(f"Response: {result['data']}")
            print(f"Status: {result['status']}")
        else:
            print(f"❌ CIB Transaction failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

asyncio.run(create_cib_transaction())
```

### CIB Transaction with Full Error Handling

```python
from sofizpay.exceptions import ValidationError, NetworkError

class CIBPaymentProcessor:
    def __init__(self):
        self.client = SofizPayClient()
    
    async def process_payment(self, 
                            account: str,
                            amount: float,
                            customer_name: str,
                            phone: str,
                            email: str,
                            memo: str = None,
                            return_url: str = None):
        """Process a CIB payment with comprehensive error handling"""
        
        # Validate inputs
        if not account or len(account) < 20:
            raise ValidationError("Invalid account number")
        
        if amount <= 0:
            raise ValidationError("Amount must be positive")
        
        transaction_data = {
            "account": account,
            "amount": amount,
            "full_name": customer_name,
            "phone": phone,
            "email": email,
            "memo": memo or f"Payment from {customer_name}",
            "return_url": return_url
        }
        
        try:
            result = await self.client.make_cib_transaction(transaction_data)
            
            if result["success"]:
                return {
                    "success": True,
                    "transaction_id": result.get("data", {}).get("id"),
                    "status": result["status"],
                    "created_at": result["timestamp"]
                }
            else:
                return {
                    "success": False,
                    "error": result["error"],
                    "status_code": result.get("status_code")
                }
                
        except ValidationError as e:
            print(f"❌ Validation error: {e}")
            raise
        except NetworkError as e:
            print(f"❌ Network error: {e}")
            raise
        except Exception as e:
            print(f"❌ Unexpected error: {e}")
            raise

# Usage
async def main():
    processor = CIBPaymentProcessor()
    
    try:
        result = await processor.process_payment(
            account="DZ1234567890123456789012",
            amount=250.00,
            customer_name="Sarah Ahmed",
            phone="+213777888999",
            email="sarah@example.com",
            memo="Subscription payment",
            return_url="https://myapp.com/success"
        )
        
        if result["success"]:
            print(f"✅ Payment processed: {result['transaction_id']}")
        else:
            print(f"❌ Payment failed: {result['error']}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

asyncio.run(main())
```

---

## 🔐 Signature Verification

### Verify SofizPay Signatures

```python
def verify_payment_callback(message: str, signature: str) -> bool:
    """Verify a payment callback from SofizPay"""
    client = SofizPayClient()
    
    verification_data = {
        "message": message,
        "signature_url_safe": signature
    }
    
    is_valid = client.verify_sofizpay_signature(verification_data)
    
    if is_valid:
        print("✅ Signature verified - payment is authentic")
        return True
    else:
        print("❌ Invalid signature - potential fraud")
        return False

# Example usage
message = "wc_order_LI3SLQ7xA7IY9cib84907success23400"
signature = "jHrONYl2NuBhjAYTgRq3xwRuW2ZYZIQlx1VWgiObu5F..."

if verify_payment_callback(message, signature):
    # Process the verified payment
    process_confirmed_payment(message)
```

### Custom Signature Verification

```python
def verify_custom_signature(message: str, signature: str, public_key_pem: str) -> bool:
    """Verify a signature with custom public key"""
    client = SofizPayClient()
    
    return client.verify_signature(
        message=message,
        signature=signature,
        public_key=public_key_pem
    )

# Example
custom_public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA...
-----END PUBLIC KEY-----"""

is_valid = verify_custom_signature("Hello World", "signature_here", custom_public_key)
```

---

## 💡 Usage Examples

### Complete Payment System

```python
import asyncio
from typing import Optional
from sofizpay import SofizPayClient
from sofizpay.exceptions import SofizPayError

class PaymentSystem:
    def __init__(self, secret_key: str):
        self.client = SofizPayClient()
        self.secret_key = secret_key
        self.public_key = self.client.get_public_key_from_secret(secret_key)
    
    async def check_balance(self) -> float:
        """Check current balance"""
        try:
            balance = await self.client.get_dzt_balance(self.public_key)
            print(f"💰 Current balance: {balance}")
            return balance
        except SofizPayError as e:
            print(f"❌ Error checking balance: {e}")
            return 0.0
    
    async def send_payment(self, 
                          destination: str, 
                          amount: str, 
                          memo: Optional[str] = None) -> bool:
        """Send a payment"""
        try:
            # Check balance first
            balance = await self.check_balance()
            if balance < float(amount):
                print(f"❌ Insufficient balance: {balance} < {amount}")
                return False
            
            # Send payment
            result = await self.client.send_payment(
                source_secret=self.secret_key,
                destination_public_key=destination,
                amount=amount,
                memo=memo
            )
            
            if result["success"]:
                print(f"✅ Payment sent successfully!")
                print(f"   Hash: {result['hash']}")
                print(f"   Amount: {amount}")
                print(f"   To: {destination}")
                return True
            else:
                print(f"❌ Payment failed: {result['error']}")
                return False
                
        except SofizPayError as e:
            print(f"❌ Payment error: {e}")
            return False
    
    async def get_transaction_history(self, limit: int = 20):
        """Get recent transactions"""
        try:
            transactions = await self.client.get_all_transactions(
                self.public_key, 
                limit=limit
            )
            
            print(f"📊 Found {len(transactions)} transactions:")
            for i, tx in enumerate(transactions[:10], 1):
                print(f"   {i}. {tx['type'].upper()}: {tx['amount']}")
                print(f"      Hash: {tx['hash'][:16]}...")
                print(f"      Date: {tx['created_at']}")
                print(f"      Memo: {tx['memo'] or 'No memo'}")
                print()
            
            return transactions
            
        except SofizPayError as e:
            print(f"❌ Error fetching transactions: {e}")
            return []
    
    async def start_monitoring(self):
        """Start real-time transaction monitoring"""
        def handle_transaction(transaction):
            amount = transaction["amount"]
            tx_type = transaction["type"]
            memo = transaction["memo"]
            
            print(f"🚨 NEW TRANSACTION DETECTED!")
            print(f"   Type: {tx_type.upper()}")
            print(f"   Amount: {amount}")
            print(f"   Memo: {memo or 'No memo'}")
            print(f"   Time: {transaction['created_at']}")
            
            # Auto-process received payments
            if tx_type == "received":
                self._process_received_payment(transaction)
        
        try:
            stream_id = await self.client.setup_transaction_stream(
                self.public_key,
                handle_transaction
            )
            print(f"📡 Started monitoring transactions...")
            return stream_id
            
        except SofizPayError as e:
            print(f"❌ Error starting monitoring: {e}")
            return None
    
    def _process_received_payment(self, transaction):
        """Process incoming payments"""
        amount = float(transaction["amount"])
        memo = transaction["memo"]
        
        if memo and "order_" in memo:
            print(f"🛒 Processing order payment: {amount}")
            # Process order...
        elif amount >= 100.0:
            print(f"💎 Large payment received: {amount}")
            # Handle large payment...
        else:
            print(f"💰 Regular payment received: {amount}")

# Usage example
async def main():
    # Initialize payment system
    payment_system = PaymentSystem("YOUR_SECRET_KEY")
    
    # Check balance
    await payment_system.check_balance()
    
    # Get transaction history
    await payment_system.get_transaction_history(limit=10)
    
    # Send a payment
    await payment_system.send_payment(
        destination="DESTINATION_PUBLIC_KEY",
        amount="5.0",
        memo="Test payment"
    )
    
    # Start monitoring (runs indefinitely)
    stream_id = await payment_system.start_monitoring()
    
    # Keep monitoring for 30 seconds
    if stream_id:
        await asyncio.sleep(30)
        payment_system.client.stop_transaction_stream(stream_id)
        print("🛑 Monitoring stopped")

# Run the example
asyncio.run(main())
```

### E-commerce Integration Example

```python
from sofizpay import SofizPayClient
from dataclasses import dataclass
from typing import Dict, Any
import asyncio

@dataclass
class Order:
    id: str
    amount: float
    customer_email: str
    description: str
    status: str = "pending"

class EcommercePaymentGateway:
    def __init__(self, merchant_secret_key: str):
        self.client = SofizPayClient()
        self.merchant_secret = merchant_secret_key
        self.merchant_public = self.client.get_public_key_from_secret(merchant_secret_key)
        self.pending_orders: Dict[str, Order] = {}
    
    async def create_payment_request(self, order: Order) -> Dict[str, Any]:
        """Create a payment request for an order"""
        # Store order
        self.pending_orders[order.id] = order
        
        # Start monitoring for this specific payment
        await self._start_order_monitoring()
        
        return {
            "order_id": order.id,
            "payment_address": self.merchant_public,
            "amount": order.amount,
            "currency": "TOKEN",
            "memo": f"order_{order.id}",
            "instructions": f"Send exactly {order.amount} to {self.merchant_public} with memo 'order_{order.id}'"
        }
    
    async def _start_order_monitoring(self):
        """Monitor for incoming payments"""
        def payment_handler(transaction):
            memo = transaction.get("memo", "")
            if memo.startswith("order_"):
                order_id = memo.replace("order_", "")
                self._process_order_payment(order_id, transaction)
        
        stream_id = await self.client.setup_transaction_stream(
            self.merchant_public,
            payment_handler
        )
        return stream_id
    
    def _process_order_payment(self, order_id: str, transaction: Dict[str, Any]):
        """Process payment for a specific order"""
        if order_id not in self.pending_orders:
            print(f"❌ Unknown order ID: {order_id}")
            return
        
        order = self.pending_orders[order_id]
        paid_amount = float(transaction["amount"])
        
        if paid_amount >= order.amount:
            order.status = "paid"
            print(f"✅ Order {order_id} paid successfully!")
            print(f"   Amount: {paid_amount}")
            print(f"   Customer: {order.customer_email}")
            
            # Send confirmation email, fulfill order, etc.
            self._fulfill_order(order)
        else:
            print(f"⚠️ Underpayment for order {order_id}")
            print(f"   Expected: {order.amount}")
            print(f"   Received: {paid_amount}")
    
    def _fulfill_order(self, order: Order):
        """Fulfill the paid order"""
        print(f"📦 Fulfilling order {order.id}: {order.description}")
        # Implement order fulfillment logic
        del self.pending_orders[order.id]

# Usage
async def ecommerce_example():
    gateway = EcommercePaymentGateway("MERCHANT_SECRET_KEY")
    
    # Create an order
    order = Order(
        id="ORD-12345",
        amount=25.50,
        customer_email="customer@example.com",
        description="Premium Subscription"
    )
    
    # Create payment request
    payment_info = await gateway.create_payment_request(order)
    print("💳 Payment request created:")
    print(f"   Order ID: {payment_info['order_id']}")
    print(f"   Amount: {payment_info['amount']} {payment_info['currency']}")
    print(f"   Address: {payment_info['payment_address']}")
    print(f"   Memo: {payment_info['memo']}")
    
    # Keep monitoring for payments
    print("📡 Monitoring for payments...")
    await asyncio.sleep(60)  # Monitor for 1 minute

asyncio.run(ecommerce_example())
```

---

## ⚠️ Error Handling

### Custom Exception Types

```python
from sofizpay.exceptions import (
    SofizPayError,           # Base exception
    PaymentError,            # Payment-specific errors  
    TransactionError,        # Transaction-specific errors
    NetworkError,           # Network-related errors
    ValidationError,        # Input validation errors
    RateLimitError,         # Rate limiting errors
    InsufficientBalanceError, # Insufficient balance
    InvalidAccountError,    # Invalid account errors
    InvalidAssetError       # Invalid asset errors
)
```

### Comprehensive Error Handling

```python
async def robust_payment_handler():
    client = SofizPayClient()
    
    try:
        result = await client.send_payment(
            source_secret="SECRET_KEY",
            destination_public_key="DEST_KEY",
            amount="10.0",
            memo="Test payment"
        )
        
        if result["success"]:
            print(f"✅ Payment successful: {result['hash']}")
        else:
            print(f"❌ Payment failed: {result['error']}")
            
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        # Handle validation errors (invalid keys, amounts, etc.)
        
    except InsufficientBalanceError as e:
        print(f"❌ Insufficient balance: {e}")
        # Handle insufficient balance
        
    except NetworkError as e:
        print(f"❌ Network error: {e}")
        # Handle network issues, retry logic
        
    except RateLimitError as e:
        print(f"❌ Rate limit exceeded: {e}")
        # Handle rate limiting, implement backoff
        
    except PaymentError as e:
        print(f"❌ Payment error: {e}")
        # Handle general payment errors
        
    except SofizPayError as e:
        print(f"❌ SofizPay error: {e}")
        # Handle any SofizPay-related error
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        # Handle unexpected errors
```

### Async Context Manager

```python
async def safe_payment_operations():
    """Use async context manager for automatic cleanup"""
    async with SofizPayClient() as client:
        # All operations here
        balance = await client.get_dzt_balance("PUBLIC_KEY")
        
        if balance > 10.0:
            result = await client.send_payment(
                source_secret="SECRET_KEY",
                destination_public_key="DEST_KEY", 
                amount="5.0"
            )
            print(f"Payment result: {result}")
    
    # Client automatically cleaned up
    print("✅ Operations completed and cleaned up")

asyncio.run(safe_payment_operations())
```

---

## 🏆 Best Practices

### Security Best Practices

```python
import os
from cryptography.fernet import Fernet

class SecureConfig:
    """Secure configuration management"""
    
    @staticmethod
    def get_secret_key() -> str:
        """Get secret key from environment or secure storage"""
        # ✅ Use environment variables
        secret_key = os.getenv('SOFIZPAY_SECRET_KEY')
        if not secret_key:
            raise ValueError("SOFIZPAY_SECRET_KEY not found in environment")
        return secret_key
    
    @staticmethod
    def encrypt_sensitive_data(data: str, key: bytes) -> str:
        """Encrypt sensitive data"""
        f = Fernet(key)
        encrypted = f.encrypt(data.encode())
        return encrypted.decode()

# ✅ Production usage
async def production_payment():
    # Get secret from secure environment
    secret_key = SecureConfig.get_secret_key()
    
    client = SofizPayClient()
    
    # Validate before processing using utils
    from sofizpay.utils import validate_secret_key
    if not validate_secret_key(secret_key):
        raise ValueError("Invalid secret key")
    
    # Process payment with error handling
    try:
        result = await client.send_payment(
            source_secret=secret_key,
            destination_public_key="DEST_KEY",
            amount="10.0"
        )
        return result
    finally:
        # Always cleanup
        del secret_key
```

### Performance Best Practices

```python
class OptimizedPaymentManager:
    def __init__(self):
        # ✅ Reuse client instance
        self.client = SofizPayClient()
        self._balance_cache = {}
        self._cache_ttl = 30  # 30 seconds
    
    async def get_cached_balance(self, public_key: str) -> float:
        """Get balance with caching"""
        import time
        now = time.time()
        
        if public_key in self._balance_cache:
            balance, timestamp = self._balance_cache[public_key]
            if now - timestamp < self._cache_ttl:
                return balance
        
        # Fetch fresh balance
        balance = await self.client.get_dzt_balance(public_key)
        self._balance_cache[public_key] = (balance, now)
        return balance
    
    async def batch_payments(self, payments: list) -> list:
        """Process multiple payments efficiently"""
        results = []
        
        # ✅ Use asyncio.gather for concurrent processing
        tasks = [
            self.client.send_payment(**payment) 
            for payment in payments
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # ✅ Cleanup resources
        self._balance_cache.clear()
```

### Validation Best Practices

```python
from typing import Union
import re

class PaymentValidator:
    """Input validation utilities"""
    
    @staticmethod
    def validate_amount(amount: Union[str, float]) -> bool:
        """Validate payment amount"""
        try:
            amount_float = float(amount)
            return (
                amount_float > 0 and 
                amount_float <= 922337203685.4775807 and  # Stellar limit
                len(str(amount).split('.')[-1]) <= 7  # Max 7 decimal places
            )
        except (ValueError, TypeError):
            return False
    
    @staticmethod  
    def validate_memo(memo: str) -> bool:
        """Validate memo field"""
        if not memo:
            return True
        return len(memo.encode('utf-8')) <= 28  # Stellar memo limit
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_memo(memo: str) -> str:
        """Sanitize memo text"""
        if not memo:
            return ""
        
        # Remove control characters
        sanitized = ''.join(char for char in memo if ord(char) >= 32)
        
        # Truncate if too long
        if len(sanitized.encode('utf-8')) > 28:
            sanitized = sanitized[:28]
        
        return sanitized

# ✅ Usage
validator = PaymentValidator()

# Validate before sending
if not validator.validate_amount("10.5"):
    raise ValueError("Invalid amount")

if not validator.validate_memo("Payment memo"):
    raise ValueError("Invalid memo")

# Sanitize inputs
clean_memo = validator.sanitize_memo(user_input_memo)
```

### Development Best Practices

```python
# ✅ Type hints for better IDE support
from typing import Dict, List, Optional, Union, Callable
import logging

# ✅ Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaymentApp:
    def __init__(self, secret_key: str):
        # ✅ Use mainnet for production
        self.client = SofizPayClient()
        self.secret_key = secret_key
        
        # ✅ Log configuration
        logger.info(f"Initialized with mainnet")
    
    async def send_payment_with_retry(self, 
                                    destination: str, 
                                    amount: str,
                                    max_retries: int = 3) -> Dict:
        """Send payment with retry logic"""
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"Payment attempt {attempt + 1}/{max_retries}")
                
                result = await self.client.send_payment(
                    source_secret=self.secret_key,
                    destination_public_key=destination,
                    amount=amount
                )
                
                if result["success"]:
                    logger.info(f"Payment successful: {result['hash']}")
                    return result
                else:
                    logger.warning(f"Payment failed: {result['error']}")
                    last_error = result["error"]
                    
            except Exception as e:
                logger.error(f"Payment attempt {attempt + 1} failed: {e}")
                last_error = str(e)
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
        return {"success": False, "error": f"All {max_retries} attempts failed. Last error: {last_error}"}

# ✅ Production usage
async def production_example():
    app = PaymentApp(os.getenv('SOFIZPAY_SECRET_KEY'))
    
    result = await app.send_payment_with_retry(
        destination="DESTINATION_PUBLIC_KEY",
        amount="1.0"
    )
    
    print(f"Result: {result}")

asyncio.run(production_example())
```

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
# Clone the repository
git clone https://github.com/sofizpay/sofizpay-sdk-python.git
cd sofizpay-sdk-python

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
python -m pytest tests/ -v

# Run linting
flake8 sofizpay/
mypy sofizpay/

# Run formatting
black sofizpay/
isort sofizpay/
```

### Contributing Process

1. **Fork** the repository
2. **Create** feature branch: `git checkout -b feature/amazing-feature`
3. **Make** your changes with tests
4. **Run** tests and linting: `pytest && flake8`
5. **Commit** changes: `git commit -m 'Add amazing feature'`
6. **Push** to branch: `git push origin feature/amazing-feature`
7. **Open** a Pull Request

### Code Standards

- ✅ Follow PEP 8 style guidelines
- ✅ Add type hints to all functions
- ✅ Write comprehensive docstrings
- ✅ Include unit tests for new features
- ✅ Maintain backwards compatibility
- ✅ Update documentation

---

## 📞 Support

- 📖 [Documentation](https://github.com/sofizpay/sofizpay-sdk-python#readme)
- 🐛 [Report Issues](https://github.com/sofizpay/sofizpay-sdk-python/issues)
- 💬 [Discussions](https://github.com/sofizpay/sofizpay-sdk-python/discussions)
- ⭐ [Star the Project](https://github.com/sofizpay/sofizpay-sdk-python)
- 📧 [Email Support](mailto:support@sofizpay.com)

### Frequently Asked Questions

**Q: How do I handle rate limiting?**
```python
# The SDK has built-in rate limiting, but you can add custom retry logic
from sofizpay.exceptions import RateLimitError
import asyncio

try:
    result = await client.send_payment(...)
except RateLimitError:
    await asyncio.sleep(60)  # Wait 1 minute
    result = await client.send_payment(...)  # Retry
```

**Q: Is the SDK thread-safe?**
```python
# Yes, but create separate client instances for different threads
import threading

def worker_thread():
    client = SofizPayClient()  # Create new instance
    # Use client in this thread...
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2025 SofizPay

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

---

## 🙏 Acknowledgments

- Built on the robust [Stellar Network](https://stellar.org)
- Powered by [stellar-sdk](https://pypi.org/project/stellar-sdk/)
- Inspired by the growing DeFi ecosystem
- Special thanks to all contributors and the open-source community

### Technical Dependencies

- **stellar-sdk**: Stellar blockchain integration
- **cryptography**: Signature verification and encryption
- **requests**: HTTP client for API calls
- **asyncio**: Asynchronous programming support

---

<div align="center">
  <p><strong>Made with ❤️ by the SofizPay Team</strong></p>
  <p>
    <a href="https://github.com/sofizpay/sofizpay-sdk-python">GitHub</a> •
    <a href="https://pypi.org/project/sofizpay-sdk-python/">PyPI</a> •
    <a href="https://github.com/sofizpay/sofizpay-sdk-python/issues">Support</a> •
    <a href="mailto:support@sofizpay.com">Contact</a>
  </p>
  
  <p>
    <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
    <img src="https://img.shields.io/badge/Stellar-Blockchain-brightgreen.svg" alt="Stellar">
  </p>
</div>
