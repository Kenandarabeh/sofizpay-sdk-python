<div align="center">
  <img src="https://github.com/kenandarabeh/sofizpay-sdk/blob/main/assets/sofizpay-logo.png?raw=true" alt="SofizPay Logo" width="200" />

  <h2>SofizPay Python SDK</h2>
  <p><strong>The official Python SDK for secure digital payments on the SofizPay platform.</strong></p>

  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
  [![PyPI](https://img.shields.io/pypi/v/sofizpay-sdk-python.svg)](https://pypi.org/project/sofizpay-sdk-python/)
</div>

---

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Core Methods](#core-methods)
- [API Reference](#api-reference)
- [Digital Services (Missions)](#digital-services-missions)
- [Bank Integration (CIB)](#bank-integration-cib)
- [Real-time Transaction Streaming](#real-time-transaction-streaming)
- [Webhook Signature Verification](#webhook-signature-verification)
- [Response Format](#response-format)
- [Security Best Practices](#security-best-practices)
- [Use Cases](#use-cases)
- [Support](#support)

---

## 🌟 Overview

The SofizPay Python SDK provides a clean **async/await** interface for integrating **DZT digital payments** into Python applications, Django backends, FastAPI services, and data scripts. Built on top of the [Stellar Python SDK](https://github.com/StellarCN/py-stellar-base), it handles on-chain payments, exhaustive transaction history, CIB bank deposits, Mission service recharges, and webhook signature verification.

**Key Benefits:**
- ⚡ Fully `async` API using `asyncio`
- 📊 Exhaustive 24-transaction history (Path Payments, Trustlines, Account Creation)
- 🔴 Real-time transaction streaming with configurable intervals
- 🏦 CIB/Dahabia bank deposit links
- 📱 Phone, Internet & Game recharges (Mission APIs)
- 🔍 RSA-based webhook signature verification

---

## 📦 Installation

```bash
pip install sofizpay-sdk-python
```

**Requirements:**
- Python `>= 3.8`
- `stellar-sdk` (auto-installed)
- `aiohttp` (auto-installed)
- `cryptography` (for signature verification)

---

## 🚀 Quick Start

```python
import asyncio
from sofizpay.client import SofizPayClient

async def main():
    client = SofizPayClient()

    # 1. Check DZT balance
    balance = await client.get_balance('YOUR_PUBLIC_KEY')
    if balance.get('success'):
        print(f"💰 Balance: {balance['balance']} DZT")

    # 2. Send a DZT payment
    result = await client.send_payment(
        source_secret='YOUR_SECRET_KEY',
        destination_public_key='RECIPIENT_PUBLIC_KEY',
        amount='100',
        memo='Invoice #1234'
    )

    if result.get('success'):
        print(f"✅ Payment sent! TX: {result['transactionHash']}")
    else:
        print(f"❌ Failed: {result.get('error')}")

asyncio.run(main())
```

---

## 🔧 Core Methods

### `get_balance(public_key)`

Fetches the current **DZT** balance for a given Stellar account.

```python
result = await client.get_balance('GCAZI...YOUR_PUBLIC_KEY')

# Response
{
    'success':      True,
    'balance':      '1500.0000000',
    'publicKey':    'GCAZI...',
    'asset_code':   'DZT',
    'asset_issuer': 'GCAZI7YBLIDJWIVEL7ETNAZGPP3LC24NO6KAOBWZHUERXQ7M5BC52DLV',
    'timestamp':    '2025-07-28T10:30:00.000Z'
}
```

---

### `send_payment(source_secret, destination_public_key, amount, memo?)`

Submits a DZT payment to the Stellar network.

```python
result = await client.send_payment(
    source_secret='SXXX...YOUR_SECRET_KEY',       # 56-char Stellar seed
    destination_public_key='GXXX...RECIPIENT',    # Recipient's public key
    amount='250.50',                               # Amount in DZT (string)
    memo='Order #5567'                             # Optional memo (max 28 chars)
)

# Success Response
{
    'success':            True,
    'transactionHash':    'abc123...hash',
    'amount':             '250.50',
    'memo':               'Order #5567',
    'destinationPublicKey': 'GXXX...',
    'timestamp':          '2025-07-28T10:30:00.000Z'
}
```

> ⚠️ **Memo Truncation:** Memos longer than 28 characters are automatically truncated.

---

### `get_transactions(public_key, limit?)`

Fetches **exhaustive transaction history** via the Stellar `/operations?join=transactions` endpoint. This is the reference implementation used to achieve **24-transaction parity** across all SDKs.

```python
history = await client.get_transactions('YOUR_PUBLIC_KEY', 100)

for tx in history:
    print(f"[{tx['created_at']}] {tx['type'].upper()} — {tx['amount']} {tx.get('asset_code', 'DZT')}")

# Each transaction dictionary contains:
# 'id'           → Transaction hash
# 'hash'         → Transaction hash
# 'type'         → 'sent' | 'received' | 'trustline' | 'account_created'
# 'amount'       → Amount as string
# 'from'         → Sender's public key
# 'to'           → Recipient's public key
# 'asset_code'   → 'DZT' or 'XLM'
# 'memo'         → Memo text (if any)
# 'created_at'   → ISO 8601 timestamp
# 'successful'   → bool
```

**Captured transaction types:**

| Type | Description |
|------|-------------|
| `sent` | DZT payment sent from this account |
| `received` | DZT payment received by this account |
| `trustline` | DZT trustline created (account activation) |
| `account_created` | Account funded for the first time |

---

### `get_public_key_from_secret(secret_key)`

Derives the Stellar public key from a secret key. This is a **synchronous** method (no `await` needed).

```python
public_key = client.get_public_key_from_secret('SXXX...YOUR_SECRET_KEY')
print('Derived public key:', public_key)
```

---

### `search_transactions_by_memo(public_key, memo, limit?)`

Performs a case-insensitive substring search over recent transactions.

```python
results = await client.search_transactions_by_memo(
    'YOUR_PUBLIC_KEY', 'Order #12345', 10
)

for tx in results:
    print(f"{tx['hash']} — {tx['memo']}")
```

---

### `get_transaction_by_hash(hash)`

Fetches a specific transaction by its hash.

```python
tx = await client.get_transaction_by_hash('abc123...hash')
if tx.get('found'):
    print('Amount:', tx['transaction']['amount'])
else:
    print('Transaction not found')
```

---

## 📚 API Reference

### Full Method Table

| Method | Parameters | Returns | Description |
|--------|-----------|---------|-------------|
| `send_payment(...)` | `source_secret, destination_public_key, amount, memo?` | `dict` | Submit DZT payment |
| `get_balance(public_key)` | `str` | `dict` | Get DZT balance |
| `get_public_key_from_secret(secret_key)` | `str` | `str` | Derive public key from secret |
| `get_transactions(public_key, limit?)` | `str, int` | `list[dict]` | Full transaction history |
| `get_transaction_by_hash(hash)` | `str` | `dict` | Find specific transaction |
| `search_transactions_by_memo(public_key, memo, limit?)` | `str, str, int` | `list[dict]` | Search by memo |
| `setup_transaction_stream(...)` | See streaming section | `str` (stream_id) | Start real-time monitoring |
| `stop_transaction_stream(stream_id)` | `str` | `None` | Stop monitoring |
| `make_cib_transaction(data)` | See CIB section | `dict` | Create bank payment link |
| `check_cib_status(order_number)` | `str` | `dict` | Check CIB order status |
| `recharge_phone(data)` | `{encrypted_sk, phone, operator, amount, offer}` | `dict` | Phone recharge |
| `recharge_internet(data)` | `{encrypted_sk, phone, amount, offer}` | `dict` | Internet recharge |
| `recharge_game(data)` | `{encrypted_sk, game, player_id, amount}` | `dict` | Game top-up |
| `pay_bill(data)` | `{encrypted_sk, ...}` | `dict` | Bill payment |
| `get_products()` | — | `dict` | List available services |
| `get_operation_history(enc_sk, limit, offset)` | `str, int, int` | `dict` | Mission operation history |
| `get_operation_details(op_id, enc_sk)` | `str, str` | `dict` | Single operation details |
| `verify_sofizpay_signature(data)` | `{message, signature_url_safe}` | `bool` | Validate RSA webhook |

---

## 📱 Digital Services (Missions)

Mission APIs let your users spend DZT on real-world digital services. All Mission calls require the user's `encrypted_sk` — **not** the raw secret key.

### Phone Recharge

```python
result = await client.recharge_phone({
    'encrypted_sk': 'USER_ENCRYPTED_SECRET_KEY',
    'phone':        '0661000000',
    'operator':     'Mobilis',  # 'Mobilis' | 'Djezzy' | 'Ooredoo'
    'amount':       '100',
    'offer':        'Top'       # Offer type from get_products()
})

if result.get('success'):
    print('✅ Phone recharged!', result.get('data'))
else:
    print('❌ Recharge failed:', result.get('error'))
```

### Internet Recharge (Idoom 4G)

```python
result = await client.recharge_internet({
    'encrypted_sk': 'USER_ENCRYPTED_SECRET_KEY',
    'phone':        '0661000000',
    'amount':       '200',
    'offer':        'idoom_1gb'
})
```

### Game Top-up (FreeFire, PUBG)

```python
result = await client.recharge_game({
    'encrypted_sk': 'USER_ENCRYPTED_SECRET_KEY',
    'game':         'freefire',
    'player_id':    '123456789',
    'amount':       '500'
})
```

### Bill Payment

```python
result = await client.pay_bill({
    'encrypted_sk': 'USER_ENCRYPTED_SECRET_KEY',
    'bill_type':    'electricity',
    'reference':    'REF123456',
    'amount':       '1500'
})
```

### Get Available Products

```python
products = await client.get_products()
if products.get('success'):
    for item in products['data']['products']:
        print(f"{item['name']} — {item['price']} DZT")
```

### Operation History & Details

```python
# Last 10 operations
history = await client.get_operation_history('USER_ENCRYPTED_SK', 10, 0)
if history.get('success'):
    print('Operations:', history.get('data'))

# Single operation detail
details = await client.get_operation_details('OPERATION_ID', 'USER_ENCRYPTED_SK')
```

---

## 🏦 Bank Integration (CIB)

Generate a Dahabia/CIB bank payment link for customers.

```python
result = await client.make_cib_transaction({
    'account':    'YOUR_STELLAR_PUBLIC_KEY',
    'amount':     2500,
    'full_name':  'Ahmed Benali',
    'phone':      '0661234567',
    'email':      'ahmed@example.com',
    'memo':       'Order #789',                        # Optional
    'return_url': 'https://yoursite.com/callback',     # Optional
    'redirect':   True
})

if result.get('success'):
    payment_url = result['data']['payment_url']
    print(f"Redirect customer to: {payment_url}")
else:
    print('CIB failed:', result.get('error'))
```

### Check CIB Status

```python
status = await client.check_cib_status('ORDER_NUMBER_FROM_CIB')
if status.get('success'):
    print('Status:', status['data']['status'])
```

---

## 🔴 Real-time Transaction Streaming

Monitor an account for new transactions using periodic polling.

### `setup_transaction_stream(public_key, callback, from_now?, check_interval?)`

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `public_key` | `str` | required | Stellar account to monitor |
| `callback` | `async function` | required | Called for each new transaction |
| `from_now` | `bool` | `True` | `True`: only future txs; `False`: load history first |
| `check_interval` | `int` | `30` | Polling interval in seconds (5–300) |

```python
import asyncio
from sofizpay.client import SofizPayClient

async def main():
    client = SofizPayClient()

    # Monitor only new transactions
    async def on_new_tx(tx):
        if tx.get('type') == 'received':
            print(f"💸 Received {tx['amount']} DZT from {tx['from']}")

    stream_id = await client.setup_transaction_stream(
        'YOUR_PUBLIC_KEY',
        on_new_tx,
        from_now=True,
        check_interval=15
    )

    # Keep running for 5 minutes
    await asyncio.sleep(300)

    # Stop the stream
    client.stop_transaction_stream(stream_id)

asyncio.run(main())
```

```python
# Load history first, then monitor new transactions
async def on_tx(tx):
    if tx.get('isHistorical'):
        print('Historical:', tx['hash'])
    else:
        print('New live transaction:', tx['hash'])

stream_id = await client.setup_transaction_stream(
    'YOUR_PUBLIC_KEY',
    on_tx,
    from_now=False,    # Load history first
    check_interval=30
)
```

---

## 🔒 Webhook Signature Verification

SofizPay signs all webhook payloads with RSA-SHA256. Always verify signatures before processing payment events.

```python
from sofizpay.client import SofizPayClient

client = SofizPayClient()

# FastAPI webhook handler example
from fastapi import FastAPI, Request, HTTPException

app = FastAPI()

@app.post('/webhook/sofizpay')
async def sofizpay_webhook(request: Request):
    payload = await request.json()

    is_valid = client.verify_sofizpay_signature({
        'message':            payload.get('message'),
        'signature_url_safe': payload.get('signature_url_safe')
    })

    if not is_valid:
        raise HTTPException(status_code=400, detail='Invalid signature')

    # ✅ Process the verified payment event
    print('Confirmed payment event:', payload.get('message'))
    return {'status': 'received'}
```

---

## 📤 Response Format

Most methods return a dictionary with a `success` key:

```python
# ✅ Success
{
    'success':   True,
    # ... method-specific fields
    'timestamp': '2025-07-28T10:30:00.000Z'
}

# ❌ Failure
{
    'success':   False,
    'error':     'Human-readable error description',
    'timestamp': '2025-07-28T10:30:00.000Z'
}
```

> Note: `get_transactions()` and `search_transactions_by_memo()` return a list directly. Check for an empty list as the failure case.

Always guard with:

```python
result = await client.get_balance('GXXX...')
if result.get('success'):
    print(result['balance'])
else:
    print('Error:', result.get('error'))
```

---

## 🛡️ Security Best Practices

| Rule | Why |
|------|-----|
| ❌ Never hardcode secret keys | Source code is often committed to version control |
| ✅ Use environment variables | `os.getenv('SOFIZPAY_SECRET')` |
| ✅ Verify webhook signatures | Prevent forged payment events |
| ✅ Use `encrypted_sk` for Missions | Protects the underlying secret key |
| ✅ Run on backend only | Never expose secret keys to clients |

```python
import os
from sofizpay.client import SofizPayClient

client = SofizPayClient()

# ✅ Correct
result = await client.send_payment(
    source_secret=os.getenv('SOFIZPAY_SECRET_KEY'),
    destination_public_key='GXXX...',
    amount='100'
)

# ❌ Never do this
result = await client.send_payment(
    source_secret='SXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
    ...
)
```

---

## 💡 Use Cases

### Django Payment View

```python
import os
import asyncio
from django.http import JsonResponse
from sofizpay.client import SofizPayClient

client = SofizPayClient()

def process_payment(request):
    order_id = request.POST.get('order_id')
    recipient = request.POST.get('recipient_key')
    amount = request.POST.get('amount')

    result = asyncio.run(client.send_payment(
        source_secret=os.getenv('SOFIZPAY_SECRET_KEY'),
        destination_public_key=recipient,
        amount=amount,
        memo=f'Order #{order_id}'
    ))

    if result.get('success'):
        return JsonResponse({'status': 'paid', 'hash': result['transactionHash']})
    else:
        return JsonResponse({'status': 'failed', 'error': result.get('error')}, status=400)
```

### Batch Payment Processing

```python
async def batch_pay(payments: list):
    results = await asyncio.gather(*[
        client.send_payment(**p) for p in payments
    ])
    success = sum(1 for r in results if r.get('success'))
    print(f"✅ {success}/{len(results)} payments succeeded")
```

---

## 📞 Support

- 🌐 **Website**: [SofizPay.com](https://sofizpay.com)
- 📚 **Full Docs**: [GitHub Repository](https://github.com/kenandarabeh/sofizpay-sdk-python#readme)
- 🐛 **Bug Reports**: [Open an Issue](https://github.com/kenandarabeh/sofizpay-sdk-python/issues)
- 💬 **Discussions**: [Community Forum](https://github.com/kenandarabeh/sofizpay-sdk-python/discussions)

---

## License

MIT © [SofizPay Team](https://github.com/kenandarabeh)

---

**Built with ❤️ for Python & Django developers | Version `1.1.0`**
