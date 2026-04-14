import asyncio
import json
from sofizpay.client import SofizPayClient

async def main():
    # 1. Initialize client in Sandbox Mode
    client = SofizPayClient(sandbox=True)
    
    print("--- Starting SofizPay Python SDK Sandbox Test ---")
    print("Current Mode: SANDBOX\n")
    
    # 2. Test make_sandbox_cib_transaction
    print("1. Testing make_sandbox_cib_transaction (Dedicated)...")
    transaction_data = {
        "account": "GB3R3DRQXBPSC2XSFLPDRVCAVRCVJXAPJGBPMJ45JBRJC5QJPM7QTUSO",
        "amount": 120.25,
        "full_name": "Python Sandbox Tester",
        "phone": "+213000000000",
        "email": "python_test@sofizpay.com",
        "memo": "Python Sandbox Test"
    }
    
    result = await client.make_sandbox_cib_transaction(transaction_data)
    print(f"Result: {json.dumps(result, indent=2)}\n")
    
    # 3. Test check_sandbox_cib_status
    if result.get('success') and 'data' in result and isinstance(result['data'], dict) and result['data'].get('cib_transaction_id'):
        cib_transaction_id = result['data']['cib_transaction_id']
        print(f"2. Testing check_sandbox_cib_status for ID: {cib_transaction_id}...")
        status = await client.check_sandbox_cib_status(cib_transaction_id)
        print(f"Status Result: {json.dumps(status, indent=2)}\n")
    else:
        print("2. Skipping check_cib_status (no order number received).\n")
        
    print("--- Sandbox Test Completed ---")

if __name__ == "__main__":
    asyncio.run(main())
