<div align="center">
  <img src="https://github.com/kenandarabeh/sofizpay-sdk/blob/main/assets/sofizpay-logo.png?raw=true" alt="SofizPay Logo" width="200" />
</div>

# SofizPay SDK Python

**The official Python SDK for secure digital payments and transactions.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Quick Start

### Installation

```bash
pip install sofizpay-sdk-python
```

### Basic Usage

```python
from sofizpay.client import SofizPayClient
import asyncio

async def main():
    client = SofizPayClient()
    result = await client.send_payment(
        source_secret='YOUR_SECRET_KEY',
        destination_public_key='RECIPIENT_PUBLIC_KEY',
        amount='100',
        memo='Payment description'
    )
    print('Payment sent!' if result.get('success') else result.get('error'))

asyncio.run(main())
```

## Features

- ✅ **Send Secure Payments** - Instant digital transactions
- ✅ **Get Account Balance** - Real-time balance checking
- ✅ **Transaction History** - Complete transaction records
- ✅ **Search & Filter** - Find transactions by memo or hash
- ✅ **Real-time Streaming** - Live transaction notifications with flexible options
- ✅ **Multi-platform** - Works everywhere (Linux, Windows, Mac)
- ✅ **Flexible Monitoring** - Stream from now or with full history, customizable intervals

## Usage Examples

### Basic Payment
```python
from sofizpay.client import SofizPayClient
import asyncio

async def main():
    client = SofizPayClient()
    result = await client.send_payment(
        source_secret='YOUR_SECRET_KEY',
        destination_public_key='RECIPIENT_PUBLIC_KEY',
        amount='50',
        memo='Web payment'
    )
    print(result)

asyncio.run(main())
```

### Get Balance
```python
from sofizpay.client import SofizPayClient
import asyncio

async def main():
    client = SofizPayClient()
    balance = await client.get_balance('YOUR_PUBLIC_KEY')
    print('Current balance:', balance)

asyncio.run(main())
```

### Transaction Streaming
```python
from sofizpay.client import SofizPayClient
import asyncio

async def main():
    client = SofizPayClient()
    async def handle_transaction(tx):
        print('New transaction:', tx)
    stream_id = await client.setup_transaction_stream(
        'YOUR_PUBLIC_KEY',
        handle_transaction,
        from_now=True,
        check_interval=30
    )
    await asyncio.sleep(120)
    client.stop_transaction_stream(stream_id)

asyncio.run(main())
```

## API Reference

### Core Methods

| Method | Description | Example |
|--------|-------------|---------|
| `send_payment(...)` | Send secure payment | `await client.send_payment(...)` |
| `get_balance(public_key)` | Get account balance | `await client.get_balance('GXXX...')` |
| `get_transactions(public_key, limit)` | Get transaction history | `await client.get_transactions('GXXX...', 50)` |
| `get_transaction_by_hash(hash)` | Find transaction by hash | `await client.get_transaction_by_hash('abc123...')` |
| `search_transactions_by_memo(public_key, memo, limit)` | Search by memo | `await client.search_transactions_by_memo('GXXX...', 'payment', 50)` |
| `get_public_key_from_secret(secret_key)` | Get public key from secret key | `client.get_public_key_from_secret('SXXX...')` |
| `setup_transaction_stream(public_key, callback, from_now, check_interval)` | Start real-time monitoring | `await client.setup_transaction_stream('GXXX...', callback, True, 30)` |
| `stop_transaction_stream(stream_id)` | Stop real-time monitoring | `client.stop_transaction_stream(stream_id)` |
| `make_cib_transaction(transaction_data)` | Create bank transaction | `await client.make_cib_transaction({...})` |
| `verify_sofizpay_signature(verification_data)` | Verify digital signature | `client.verify_sofizpay_signature({...})` |

### Bank Transaction Parameters

```python
transaction_data = {
    'account': 'string',          # User account public key
    'amount': 100,               # Transaction amount (must be > 0)
    'full_name': 'string',       # Customer full name
    'phone': 'string',           # Customer phone number
    'email': 'string',           # Customer email address
    # Optional
    'memo': 'string',            # Transaction description/memo
    'return_url': 'string',      # URL to redirect after payment
    'redirect': True             # Whether to redirect automatically
}
```

### Signature Verification Parameters

```python
verification_data = {
    'message': 'string',              # Original message to verify
    'signature_url_safe': 'string'    # Base64URL-encoded signature
}
```

### Advanced Features

```python
# Get public key from secret key
public_key = client.get_public_key_from_secret('YOUR_SECRET_KEY')
print('Public key:', public_key)

# Real-time transaction monitoring - New transactions only
async def handle_new(tx):
    print('New transaction received:', tx)
await client.setup_transaction_stream('YOUR_PUBLIC_KEY', handle_new, True, 30)

# Real-time monitoring with full history first
async def handle_all(tx):
    if tx.get('isHistorical'):
        print('Historical transaction:', tx)
    else:
        print('New transaction received:', tx)
await client.setup_transaction_stream('YOUR_PUBLIC_KEY', handle_all, False, 15)

# Stop monitoring
client.stop_transaction_stream(stream_id)

# Search transactions by memo with custom limit
results = await client.search_transactions_by_memo('YOUR_PUBLIC_KEY', 'payment', 100)
if results:
    print('Found transactions:', results)

# Get specific transaction by hash
transaction = await client.get_transaction_by_hash('TRANSACTION_HASH_HERE')
print('Transaction details:', transaction)
```

### Utility Functions

```python
# Convert secret key to public key
public_key = client.get_public_key_from_secret('SXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
print('Derived public key:', public_key)

# Get complete transaction history with custom limit
all_transactions = await client.get_transactions('YOUR_PUBLIC_KEY', 200)
print(f'Found {len(all_transactions)} transactions')
for tx in all_transactions:
    print(f"{tx['type']}: {tx['amount']} - {tx['memo']} ({tx['created_at']})")

# Search for specific payments by memo
order_payments = await client.search_transactions_by_memo('YOUR_PUBLIC_KEY', 'Order #12345', 10)
if order_payments:
    print('Found order payments:', order_payments)
else:
    print('No payments found for this order')
```

### Bank Integration

```python
bank_result = await client.make_cib_transaction({
    'account': 'YOUR_PUBLIC_KEY',
    'amount': 150,
    'full_name': 'Ahmed',
    'phone': '+213*********',
    'email': 'ahmed@sofizpay.com',
    'memo': 'Payment',
    'return_url': 'https://yoursite.com/payment-success',
    'redirect': True
})

if bank_result.get('success'):
    print('Bank transaction created:', bank_result.get('url'))
else:
    print('Bank transaction failed:', bank_result.get('error'))
```

### Real-time Streaming Options

The `setup_transaction_stream` method accepts these parameters:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `public_key` | `str` | - | **Required**. Account public key to monitor |
| `callback` | `function` | - | **Required**. Function called for each transaction |
| `from_now` | `bool` | `True` | `True`: Only new transactions, `False`: Load history then monitor |
| `check_interval` | `int` | `30` | Reconnection interval in seconds (5-300) |

```python
# Example: Load last 200 transactions then monitor new ones
await client.setup_transaction_stream(
    'GXXX...', 
    lambda tx: print(tx), 
    False,  # Load historical transactions first
    10      # Check every 10 seconds
)

# Example: Monitor only new transactions with custom interval
await client.setup_transaction_stream(
    'GXXX...', 
    lambda tx: print('Live transaction:', tx), 
    True,   # From now only
    60      # Check every minute
)
```

### Digital Signature Verification

```python
# Verify digital signature 
is_valid = client.verify_sofizpay_signature({
    'message': 'wc_order_LI3SLQ7xA7IY9cib84907success23400',
    'signature_url_safe': 'jHrONYl2NuBhjAYTgRq3xwRuW2ZYZIQlx1VWgiObu5FrSnY78pQ...'
})

if is_valid:
    print('Signature is valid - proceed with order')
else:
    print('Invalid signature - reject request')
```

## Response Format

All methods return a consistent response format:

```python
# Success
{
  'success': True,
  # ... method-specific data
  'timestamp': "2025-07-28T10:30:00.000Z"
}

# Error
{
  'success': False,
  'error': "Error description",
  'timestamp': "2025-07-28T10:30:00.000Z"
}
```

## Configuration

The SDK is pre-configured for secure digital transactions:

- **Network**: Mainnet
- **Security**: Enterprise-grade encryption
- **Performance**: Optimized for high-throughput operations

## Security Best Practices

⚠️ **Important Security Notes:**

- Never expose secret keys in client-side code
- Use environment variables for sensitive data
- Always test on test environment first
- Validate all inputs before sending transactions

```python
# ✅ Good - Environment variable
import os
secret_key = os.getenv('SECRET_KEY')

# ❌ Bad - Hardcoded in code
secret_key = 'SXXXXXXXXXXXXX...'
```

## Transaction Flow

```mermaid
graph TD
    A[Initialize SDK] --> B[Authenticate]
    B --> C{Transaction Type}
    C -->|Payment| D[Submit Payment]
    C -->|Query| E[Get Balance/History]
    C -->|Stream| F[Monitor Real-time]
    D --> G[Payment Processing]
    E --> H[Return Data]
    F --> I[Live Updates]
    G --> J[Success/Error Response]
```

## Examples Repository

Find complete examples at: [github.com/kenandarabeh/sofizpay-sdk-python/examples](https://github.com/kenandarabeh/sofizpay-sdk-python/tree/main/examples)

## Support

- 📚 **Documentation**: [Full API Docs](https://github.com/kenandarabeh/sofizpay-sdk-python#readme)
- 🐛 **Issues**: [Report Bug](https://github.com/kenandarabeh/sofizpay-sdk-python/issues)
- 💬 **Discussions**: [Community Help](https://github.com/kenandarabeh/sofizpay-sdk-python/discussions)
- 🌐 **Website**: [SofizPay.com](https://sofizpay.com)

## Use Cases

### E-commerce Integration
Perfect for online stores needing secure payment processing:
```python
# Process customer payment
result = await client.send_payment(
  source_secret=os.getenv('STORE_SECRET_KEY'),
  destination_public_key=customer_key,
  amount=order_total,
  memo=f"Order #{order_id}"
)
```

### Financial Applications
Built for fintech apps requiring real-time transaction monitoring:
```python
# Monitor account activity
await client.setup_transaction_stream(user_key, lambda tx: print(tx), True, 30)
```

### Enterprise Solutions
Scalable for high-volume business operations:
```python
# Batch processing
results = await asyncio.gather(*[
  client.send_payment(**payment) for payment in payments
])
```

## Performance

- **Speed**: Sub-second transaction processing
- **Reliability**: 99.9% uptime guarantee
- **Scalability**: Handles thousands of transactions per second
- **Global**: Worldwide transaction support

## License

MIT © [SofizPay Team](https://github.com/kenandarabeh)

---

**Built with ❤️ for Sofizpay**
