import asyncio
import json
from sofizpay.client import SofizPayClient

async def test_all():
    # Test Credentials
    pub = "GB3R3DRQXBPSC2XSFLPDRVCAVRCVJXAPJGBPMJ45JBRJC5QJPM7QTUSO"
    enc_sk = "SCILSE4IMSKSZ7PPDP26CXOYFXWLUER47X5ROMYE6XLWSCZX2UPFKBCO"
    tx_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    client = SofizPayClient()
    print(f"--- Starting SofizPay Python SDK Test (v{client.VERSION}) ---")

    try:
        # 1. Core: Fetch Balance
        balance = await client.get_balance(pub)
        print(f"1. Get Balance: {balance}")

        # 2. Core: Transaction History
        transactions_result = await client.get_transactions(pub)
        print(f"2. Get Transactions: {len(transactions_result.get('transactions', []))} found")

        # 3. Core: Public Key Discovery
        # get_public_key_from_secret is sync
        try:
            pk = client.get_public_key_from_secret(pub)
            print(f"3. Get Public Key (Validation): Success")
        except:
            print(f"3. Get Public Key (Validation): Expected fail (mock key)")

        # 4. Core: Search Transactions by Memo
        search_result = await client.search_transactions_by_memo(pub, memo="test")
        print(f"4. Search Transactions by Memo: {len(search_result.get('transactions', []))} found")

        # 5. Core: Transaction by Hash
        tx_details = await client.get_transaction_by_hash(tx_hash)
        print(f"5. Get Transaction by Hash: Found={tx_details.get('found')}")

        # 6. CIB: Create Transaction
        cib_create = await client.make_cib_transaction({
            "account": pub,
            "amount": 100.0,
            "full_name": "Python SDK Tester",
            "phone": "0661000000",
            "email": "test@sofizpay.com",
            "memo": "Test CIB Pay"
        })
        print(f"6. CIB Create: Success={cib_create.get('success')}")

        # 7. CIB: Check Status
        if cib_create.get('success') and 'data' in cib_create and isinstance(cib_create['data'], dict):
            order_no = cib_create['data'].get('order_number')
            if order_no:
                status = await client.check_cib_status(order_no)
                print(f"7. CIB Status: Success={status.get('success')}")
        else:
            print("7. CIB Status: Skipped (no order number)")

        # 8. Services: Get Products
        products = await client.get_products(enc_sk)
        print(f"8. Get Products: Success={products.get('success')}")

        # 9. Services: Operation History
        history = await client.get_operation_history(enc_sk, limit=10)
        print(f"9. Operation History: Success={history.get('success')}")

        # 10. Services: Operation Details
        details = await client.get_operation_details("OP_12345", enc_sk)
        print(f"10. Operation Details: Success={details.get('success')}")

        # 11. Mission: Phone Recharge
        recharge = await client.recharge_phone({
            "encrypted_sk": enc_sk,
            "phone": "0661000000",
            "operator": "mobilis",
            "amount": 100,
            "offer": "pix"
        })
        print(f"11. Recharge Phone: Success={recharge.get('success')}")

        # 12. Mission: Internet Recharge
        internet = await client.recharge_internet({
            "encrypted_sk": enc_sk,
            "phone": "0661000000",
            "operator": "idoom",
            "amount": 2000,
            "offer": "adsl"
        })
        print(f"12. Recharge Internet: Success={internet.get('success')}")

        # 13. Mission: Game Recharge
        game = await client.recharge_game({
            "encrypted_sk": enc_sk,
            "operator": "freefire",
            "playerId": "123456789",
            "amount": 100,
            "offer": "diamonds"
        })
        print(f"13. Recharge Game: Success={game.get('success')}")

        # 14. Mission: Pay Bill
        bill = await client.pay_bill({
            "encrypted_sk": enc_sk,
            "operator": "sonelgaz",
            "bill_id": "BILL_999",
            "amount": 5500
        })
        print(f"14. Pay Bill: Success={bill.get('success')}")

        # 15. Utility: Signature Verification
        is_valid = client.verify_sofizpay_signature({
            "message": "test_message",
            "signature_url_safe": "jHrONYl2NuBhjAYTgRq3xwRuW2ZYZIQlx1VWgiObu5FrSnY78pQ"
        })
        print(f"15. Signature Verification: {is_valid}")

        # 16. Stream: Monitoring
        print("16. Stream - Setting up...")
        def handle_tx(tx):
            print(f"STREAM EVENT: {tx.get('hash')}")
        
        stream_id = await client.setup_transaction_stream(pub, handle_tx, from_now=True, check_interval=15)
        print(f"Stream started with ID: {stream_id}")
        
        # Stop stream
        stopped = client.stop_transaction_stream(stream_id)
        print(f"Stream stopped: {stopped}")

    except Exception as e:
        print(f"Critical Test Failure: {str(e)}")

    print("--- SDK Test Completed ---")

if __name__ == "__main__":
    asyncio.run(test_all())
