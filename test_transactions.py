import asyncio
from sofizpay.transactions import TransactionManager
import time

async def main():
    # Use the same public key used in JS tests
    public_key = "GDNS27ISCGOIJFXC6CM4O5SVHVJPSWR42QEBWUFF24N5VVHGW73ZSJNQ"
    
    print(f"--- SofizPay Python SDK: Testing get_transactions ---")
    print(f"Public Key: {public_key}")
    print("-" * 50)
    
    manager = TransactionManager()
    
    start_time = time.time()
    try:
        # Fetch all transactions
        transactions = await manager.get_transactions(public_key)
        duration = time.time() - start_time
        
        print(f"✅ Success! Fetched {len(transactions)} DZT transactions.")
        print(f"⏱️ Duration: {duration:.2f} seconds")
        print("-" * 50)
        
        if transactions:
            # Show all transactions with full response
            for i, tx in enumerate(transactions):
                print(f"[{i}] {tx}")
        
    except Exception as e:
        print(f"❌ Failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
