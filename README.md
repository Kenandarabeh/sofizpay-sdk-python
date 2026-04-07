<div align="center">
  <img src="https://github.com/kenandarabeh/sofizpay-sdk/blob/main/assets/sofizpay-logo.png?raw=true" alt="SofizPay Logo" width="200" />

  <h2>SofizPay Python SDK</h2>
  <p><strong>The official Python SDK for secure digital payments on the SofizPay platform.</strong></p>

  [![PyPI version](https://badge.fury.io/py/sofizpay-sdk-python.svg)](https://pypi.org/project/sofizpay-sdk-python/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Methods](#core-methods)
- [Digital Services (Missions)](#digital-services-missions)
- [Bank Integration (CIB)](#bank-integration-cib)
- [Real-time Transaction Streaming](#real-time-transaction-streaming)
- [Response Format](#response-format)
- [Security Best Practices](#security-best-practices)
- [Support](#support)

---

## 🌟 Overview

The SofizPay Python SDK provides a complete `async` interface for integrating **DZT digital payments** into Python applications, Django backends, and FastAPI services. It offers high-level abstractions for Stellar payments, transaction history, and digital service recharges.

**Key Benefits:**
- ⚡ **Fully Async:** Built on `aiohttp` for non-blocking I/O
- 🌍 **Framework Agnostic:** Works perfectly with Django, FastAPI, Flask, or CLI tools
- 📊 **Exhaustive History:** Captures Path Payments, Trustlines, and account events
- 🏦 **CIB/Dahabia:** Simple bank deposit link generation
- 📱 **Missions:** Phone, Internet, and Game top-ups via Mission APIs

---

## 📦 Installation

### pip

```bash
pip install sofizpay-sdk-python
```

**Requirements:** 
- Python `>= 3.8`
- Dependencies: `aiohttp`, `stellar-sdk`

---

## 🚀 Quick Start

```python
import asyncio, os
from sofizpay.client import SofizPayClient

async def main():
    client = SofizPayClient()

    # 1. Check DZT balance
    balance = await client.get_balance('YOUR_PUBLIC_KEY')
    if balance['success']:
        print(f"💰 Balance: {balance['balance']} DZT")

    # 2. Send a DZT payment
    result = await client.send_payment(
        source_secret='YOUR_SECRET_KEY',
        destination_public_key='RECIPIENT_PUBLIC_KEY',
        amount='100',
        memo='Invoice #1234'
    )

    if result.get('success'):
        print(f"✅ Payment sent! Hash: {result['transactionHash']}")
    else:
        print(f"❌ Error: {result.get('error')}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 🔧 Core Methods

### `get_balance(public_key)`

Returns the current **DZT** balance for a given Stellar account.

```python
result = await client.get_balance('GCAZI...YOUR_PUBLIC_KEY')

# Response
{
  'success':      True,
  'balance':      '1500.0000000',
  'publicKey':    'GCAZI...',
  'asset_code':   'DZT',
  'asset_issuer': 'GCAZI7YBLIDJWIVEL7ETNAZGPP3LC24NO6KAOBWZHUERXQ7M5BC52DLV',
  'timestamp':    '2025-07-28T10:30:00Z'
}
```

---

### `send_payment(source_secret, destination_public_key, amount, memo?)`

Submits a DZT payment to the Stellar network.

```python
result = await client.send_payment(
    source_secret='SXXX...YOUR_SECRET',           # 56-char Stellar seed
    destination_public_key='GXXX...RECIPIENT',
    amount='250.50',                              # Amount in DZT
    memo='Order #5567'                            # Optional, max 28 chars
)

# Success Response
{
  'success':            True,
  'transactionId':      'abc123...hash',
  'transactionHash':    'abc123...hash',
  'amount':             '250.50',
  'memo':               'Order #5567',
  'destinationPublicKey': 'GXXX...',
  'timestamp':          '2025-07-28T10:30:00Z'
}
```

> ⚠️ **Memo Truncation:** Memos longer than 28 characters are automatically truncated.

---

### `get_transactions(public_key, limit?)`

Fetches **exhaustive transaction history** via Stellar. Includes payments, trustlines, and account creation.

```python
transactions = await client.get_transactions('YOUR_PUBLIC_KEY', 100)

for tx in transactions:
    print(f"[{tx['created_at']}] {tx['type']} — {tx['amount']} DZT")
```

---

### `search_transactions_by_memo(public_key, memo, limit?)`

Performs a case-insensitive search over recent transactions.

```python
results = await client.search_transactions_by_memo('YOUR_PUBLIC_KEY', 'Order #1234', 10)
if results['success']:
    print(f"Found {results['totalFound']} matches")
```

---

## 📱 Digital Services (Missions)

Mission APIs allow users to spend DZT on real-world digital services. All calls require `encrypted_sk`.

### Phone Recharge

```python
result = await client.recharge_phone({
    'encrypted_sk': 'USER_ENCRYPTED_SECRET_KEY',
    'phone':        '0661000000',
    'operator':     'mobilis',   # 'mobilis' | 'djezzy' | 'ooredoo'
    'amount':       '100',
    'offer':        'Top'        # e.g., 'Top', 'Pix'
})

if result['success']:
    print('✅ Phone recharged:', result['data'])
```

### Internet Recharge (Idoom 4G)

```python
result = await client.recharge_internet({
    'encrypted_sk': 'USER_ENCRYPTED_SECRET_KEY',
    'phone':        '0661000000',
    'operator':     'algerie-telecom',
    'amount':       '2000',
    'offer':        'prepaid'
})
```

### Game Top-up (FreeFire, PUBG)

```python
result = await client.recharge_game({
    'encrypted_sk': 'USER_ENCRYPTED_SECRET_KEY',
    'operator':     'freefire',
    'player_id':    '123456789',
    'amount':       '500', 
    'offer':        'diamonds'
})
```

### Get Available Products

```python
products = await client.get_products()
if products.get('success'):
    print('Available services:', products['data'])
```

> [!TIP]
> Use the product `name` for the `offer` field and the product `amount` for the `amount` field.

---

## 🏦 Bank Integration (CIB)

Generate secure Dahabia/CIB bank payment links.

```python
result = await client.make_cib_transaction({
    'account':    'YOUR_STELLAR_PUBLIC_KEY',
    'amount':     2500,                         # DZD (Algerian Dinars)
    'full_name':  'Ahmed Benali',
    'phone':      '0661234567',
    'email':      'ahmed@example.com',
    'memo':       'Order #789',
    'return_url': 'https://yoursite.com/callback',
    'redirect':   'no'                          # 'yes' for auto-redirect
})

if result.get('success'):
    payment_url = result['data']['payment_url']
    print(f"Redirect customer to: {payment_url}")
```

### Check CIB Status

```python
status = await client.check_cib_status('CIB_TRANSACTION_ID')
if status['success']:
    print(f"Status: {status['data']['status']}")
```

---

## 🔴 Real-time Transaction Streaming

The Python SDK uses polling to monitor accounts for new transactions.

### `setup_transaction_stream(public_key, callback, from_now?, check_interval?)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `public_key` | `str` | required | Stellar account to monitor |
| `callback` | `async function` | required | Called for each new transaction |
| `from_now` | `bool` | `True` | `True`: new txs only; `False`: load history first |
| `check_interval` | `int` | `30` | Polling interval in seconds |

```python
async def on_tx(tx):
    print(f"New {tx['type']}: {tx['amount']} DZT — memo: {tx['memo']}")

stream_id = await client.setup_transaction_stream(
    'YOUR_PUBLIC_KEY', on_tx, from_now=True, check_interval=15
)
```

---

## 📤 Response Format

All async methods return a dictionary with a `success` flag:

```python
# ✅ Success
{
  'success':   True,
  'data':      {...}, # method-specific
  'timestamp': '2025-07-28T10:30:00Z'
}

# ❌ Failure
{
  'success':   False,
  'error':     'Error message',
  'timestamp': '2025-07-28T10:30:00Z'
}
```

---

## 🛡️ Security Best Practices

- ❌ Never expose secret keys in public repositories or client-side code.
- ✅ Use environment variables (`os.getenv('SOFIZPAY_SECRET')`).
- ✅ Keep `encrypted_sk` secure in your backend database.
- ✅ Use `encrypted_sk` for all Mission API calls (never the raw secret).
- ✅ Run payment logic on backend only.

---

## 📞 Support

- 🌐 **Website**: [SofizPay.com](https://sofizpay.com)
- 📚 **Full Docs**: [docs.sofizpay.com](https://docs.sofizpay.com)
- 🐛 **Bug Reports**: [GitHub Issues](https://github.com/kenandarabeh/sofizpay-sdk-python/issues)

---

## License

MIT © [SofizPay Team](https://github.com/kenandarabeh)

**Built with ❤️ for Python developers | Version `1.1.0`**

