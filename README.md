<div align="center">
  <img src="https://github.com/kenandarabeh/sofizpay-sdk/blob/main/assets/sofizpay-logo.png?raw=true" alt="SofizPay Logo" width="200" />

  <h2>SofizPay Python SDK</h2>
  <p><strong>The official Python SDK for secure digital payments on the SofizPay platform.</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
  [![Docs](https://img.shields.io/badge/Docs-docs.sofizpay.com-blue)](https://docs.sofizpay.com)
</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Stellar Payments (DZT)](#stellar-payments-dzt)
- [CIB Bank Payments](#cib-bank-payments)
- [Digital Services (Missions)](#digital-services-missions)
- [Operation History](#operation-history)
- [Real-time Transaction Streaming](#real-time-transaction-streaming)
- [Webhook Signature Verification](#webhook-signature-verification)
- [Response Format](#response-format)
- [Security Best Practices](#security-best-practices)
- [Support](#support)

---

## 🌟 Overview

The SofizPay Python SDK provides a complete `async` interface for integrating **DZT digital payments** into Python applications, Django backends, and FastAPI services.

📚 **Full API Reference:** [docs.sofizpay.com](https://docs.sofizpay.com)

---

## 📦 Installation

```bash
pip install sofizpay-sdk-python
```

---

## 🚀 Quick Start

```python
import asyncio, os
from sofizpay.client import SofizPayClient

async def main():
    client = SofizPayClient()

    # Check balance
    balance = await client.get_balance('YOUR_PUBLIC_KEY')
    print(f"Balance: {balance['balance']} DZT")

    # Send payment
    result = await client.send_payment(
        source_secret='YOUR_SECRET_KEY',
        destination_public_key='RECIPIENT_PUBLIC_KEY',
        amount='100',
        memo='Invoice #1234'
    )

    if result.get('success'):
        print(f"✅ TX: {result['transactionHash']}")

asyncio.run(main())
```

---

## ⭐ Stellar Payments (DZT)

### `get_balance(public_key)`

```python
result = await client.get_balance('GCAZI...YOUR_PUBLIC_KEY')
# {'success': True, 'balance': '1500.0000000', 'asset_code': 'DZT', ...}
```

### `send_payment(source_secret, destination_public_key, amount, memo?)`

```python
result = await client.send_payment(
    source_secret='SXXX...SECRET',           # 56-char Stellar seed
    destination_public_key='GXXX...RECIPIENT',
    amount='100',                             # DZT amount (as string)
    memo='Order #5567'                        # Optional, max 28 chars
)
# {'success': True, 'transactionHash': '...', 'amount': '100', ...}
```

### `get_transactions(public_key, limit?)`

Exhaustive history via Stellar `/operations?join=transactions`:

| Type | Description |
|------|-------------|
| `sent` | DZT sent from this account |
| `received` | DZT received by this account |
| `trustline` | DZT trustline setup event |
| `account_created` | Account creation / initial funding |

```python
transactions = await client.get_transactions('YOUR_PUBLIC_KEY', 100)
for tx in transactions:
    print(f"[{tx['created_at']}] {tx['type']} — {tx['amount']} DZT")
```

### Search & Lookup

```python
# Derive public key (synchronous, no await)
public_key = client.get_public_key_from_secret('SXXX...SECRET')

# Search by memo
results = await client.search_transactions_by_memo('YOUR_PUBLIC_KEY', 'Order #1234', 10)

# Get by hash
tx = await client.get_transaction_by_hash('abc123...hash')
```

---

## 🏦 CIB Bank Payments

Initiates a CIB/Dahabia bank payment and redirects the customer to the secure gateway.

**Endpoint:** `GET https://www.sofizpay.com/make-cib-transaction/`
**Sandbox:** `GET https://www.sofizpay.com/sandbox/make-cib-transaction/`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `account` | `str` | ✅ | Your merchant Stellar public key |
| `amount` | `int/float` | ✅ | Amount in Algerian Dinars (DZD) |
| `full_name` | `str` | ✅ | Customer's full name as on card |
| `phone` | `str` | ✅ | Customer's phone number |
| `email` | `str` | ✅ | Customer's email for receipt |
| `return_url` | `str` | ✅ | URL to redirect after payment |
| `memo` | `str` | ✅ | Order reference (e.g. `"Order #1234"`) |
| `redirect` | `str` | ✅ | `"yes"` → auto-redirect; `"no"` → returns URL in response |
| `keep_return_url` | `bool` | ❌ | `True` → adds RSA signature to callback |

### Example — Get Payment URL (`redirect: "no"`)

```python
result = await client.make_cib_transaction({
    'account':    'YOUR_STELLAR_PUBLIC_KEY',
    'amount':     2500,
    'full_name':  'Ahmed Benali',
    'phone':      '0661234567',
    'email':      'ahmed@example.com',
    'return_url': 'https://yoursite.com/payment/callback',
    'memo':       'Order #789',
    'redirect':   'no'    # Returns payment URL in response body
})

if result.get('success'):
    payment_url = result['data']['payment_url']
    print(f"Redirect customer to: {payment_url}")
```

### Example — Auto-redirect (`redirect: "yes"`)

```python
result = await client.make_cib_transaction({
    'account':         'YOUR_STELLAR_PUBLIC_KEY',
    'amount':          1500,
    'full_name':       'Youcef Amrani',
    'phone':           '0770000000',
    'email':           'youcef@example.com',
    'return_url':      'https://yoursite.com/payment/callback',
    'memo':            'Order #999',
    'redirect':        'yes',   # Server sends HTTP 302 redirect
    'keep_return_url': True     # Enables RSA-signed callbacks
})
```

### Check CIB Status

**Endpoint:** `GET https://www.sofizpay.com/cib-transaction-check/`

```python
status = await client.check_cib_status('ORDER_NUMBER')
print(status['data']['status'])  # 'success' | 'pending' | 'failed'
```

---

## 📱 Digital Services (Missions)

All services use `encrypted_sk` for authentication.

**Endpoint:** `POST https://www.sofizpay.com/services/operation_post`

### Phone Recharge

**Operators:** `djezzy` · `ooredoo` · `mobilis`

```python
result = await client.recharge_phone({
    'encrypted_sk': 'USER_ENCRYPTED_SK',
    'phone':        '0661000000',
    'operator':     'mobilis',   # 'djezzy' | 'ooredoo' | 'mobilis'
    'amount':       '100',
    'offer':        'prepaid'    # 'prepaid' | 'postpaid'
})
```

### Internet Recharge

**Operators:** `algerie-telecom` · `djezzy` · `ooredoo` · `mobilis`

```python
result = await client.recharge_internet({
    'encrypted_sk': 'USER_ENCRYPTED_SK',
    'phone':        '0661000000',
    'operator':     'algerie-telecom',
    'amount':       '200',
    'offer':        'prepaid'
})
```

### Game Top-up

**Games:** `freefire` · `pubg`

```python
result = await client.recharge_game({
    'encrypted_sk': 'USER_ENCRYPTED_SK',
    'operator':     'freefire',   # 'freefire' | 'pubg'
    'player_id':    '123456789',  # In-game Player ID
    'amount':       '500'
})
```

### Bill Payment

**Providers:** `ade` (Water) · `sonelgaz` (Electricity) · `algerie-telecom`

```python
result = await client.pay_bill({
    'encrypted_sk': 'USER_ENCRYPTED_SK',
    'operator':     'sonelgaz',
    'ref':          'BILL_REFERENCE',
    'amount':       '1500'
})
```

### Get Available Products

**Endpoint:** `GET https://www.sofizpay.com/services/get_products`

```python
products = await client.get_products()
if products.get('success'):
    for p in products['data']['products']:
        print(f"{p['name']} — {p['price']} DZT")
```

---

## 📋 Operation History

### Get History (paginated)

**Endpoint:** `GET https://www.sofizpay.com/operation-history/`

```python
history = await client.get_operation_history('USER_ENCRYPTED_SK', 10, 0)
# Parameters: encrypted_sk, limit, offset
```

### Get Operation Details

**Endpoint:** `GET https://www.sofizpay.com/operation-details/{id}/`

```python
details = await client.get_operation_details('OPERATION_ID', 'USER_ENCRYPTED_SK')
```

---

## 🔴 Real-time Transaction Streaming

### `setup_transaction_stream(public_key, callback, from_now?, check_interval?)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `public_key` | `str` | required | Stellar account to monitor |
| `callback` | `async function` | required | Called for each new transaction |
| `from_now` | `bool` | `True` | `True`: new txs only; `False`: load history first |
| `check_interval` | `int` | `30` | Polling interval in seconds |

```python
async def on_tx(tx):
    if tx.get('type') == 'received':
        print(f"💸 Received {tx['amount']} DZT from {tx['from']}")

stream_id = await client.setup_transaction_stream(
    'YOUR_PUBLIC_KEY', on_tx, from_now=True, check_interval=15
)

await asyncio.sleep(300)   # Monitor for 5 minutes
client.stop_transaction_stream(stream_id)
```

---

## 🔒 Webhook Signature Verification

When `keep_return_url: True` is set in a CIB transaction, SofizPay appends an RSA-SHA256 signature to the `return_url` callback. Always verify before processing.

```python
# FastAPI example
from fastapi import FastAPI, Request, HTTPException
app = FastAPI()

@app.get('/payment/callback')
async def payment_callback(request: Request):
    params = dict(request.query_params)

    is_valid = client.verify_sofizpay_signature({
        'message':            params.get('message'),
        'signature_url_safe': params.get('signature_url_safe')
    })

    if not is_valid:
        raise HTTPException(status_code=400, detail='Invalid signature')

    # ✅ Process the confirmed payment
    return {'status': 'received'}
```

---

## 📤 Response Format

```python
# ✅ Success
{'success': True, 'data': {...}, 'timestamp': '...'}

# ❌ Failure
{'success': False, 'error': 'Message', 'timestamp': '...'}
```

> Note: `get_transactions()` returns a list directly. Check for empty list as the error case.

---

## 🛡️ Security Best Practices

- ❌ Never hardcode secret keys in source files
- ✅ Use `os.getenv('SOFIZPAY_SECRET')` 
- ✅ Always call `verify_sofizpay_signature()` on CIB callbacks
- ✅ Use `encrypted_sk` for all Mission API calls (never the raw secret)
- ✅ Run payment logic on backend only — never expose keys to clients

---

## 📞 Support

- 🌐 **Website**: [SofizPay.com](https://sofizpay.com)
- 📚 **Official Docs**: [docs.sofizpay.com](https://docs.sofizpay.com)
- 🐛 **Issues**: [GitHub Issues](https://github.com/kenandarabeh/sofizpay-sdk-python/issues)

---

MIT © [SofizPay Team](https://github.com/kenandarabeh) | **Version `1.1.0`**
