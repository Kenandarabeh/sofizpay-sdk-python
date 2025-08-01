"""Main SofizPay SDK client"""

import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
import requests
import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature

from .payments import PaymentManager
from .transactions import TransactionManager
from .exceptions import SofizPayError, ValidationError, NetworkError


class SofizPayClient:
    """
    Main client for SofizPay SDK
    
    This class provides a unified interface for all SofizPay operations
    including payments, transaction monitoring, balance management,
    CIB transactions, and signature verification.
    """
    
    VERSION = "1.0.2"
    
    SOFIZPAY_PUBLIC_KEY_PEM = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA1N+bDPxpqeB9QB0affr/
02aeRXAAnqHuLrgiUlVNdXtF7t+2w8pnEg+m9RRlc+4YEY6UyKTUjVe6k7v2p8Jj
UItk/fMNOEg/zY222EbqsKZ2mF4hzqgyJ3QHPXjZEEqABkbcYVv4ZyV2Wq0x0ykI
+Hy/5YWKeah4RP2uEML1FlXGpuacnMXpW6n36dne3fUN+OzILGefeRpmpnSGO5+i
JmpF2mRdKL3hs9WgaLSg6uQyrQuJA9xqcCpUmpNbIGYXN9QZxjdyRGnxivTE8awx
THV3WRcKrP2krz3ruRGF6yP6PVHEuPc0YDLsYjV5uhfs7JtIksNKhRRAQ16bAsj/
9wIDAQAB
-----END PUBLIC KEY-----"""
    
    def __init__(self, server_url: str = "https://horizon.stellar.org"):
        """
        Initialize SofizPay client
        
        Args:
            server_url: Stellar Horizon server URL (defaults to mainnet)
        """
        self.server_url = server_url
        self.payment_manager = PaymentManager(server_url)
        self.transaction_manager = TransactionManager(server_url)
    
    async def send_payment(
        self,
        source_secret: str,
        destination_public_key: str,
        amount: str,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a payment on Sofizpay
        
        Args:
            source_secret: Secret key of the source account
            destination_public_key: Public key of the destination account
            amount: Amount to send (as string)
            memo: Optional memo to attach to transaction
            
        Returns:
            Dictionary with transaction result
            
        Example:
            ```python
            client = SofizPayClient()
            result = await client.send_payment(
                source_secret="SECRET_KEY_HERE",
                destination_public_key="DEST_PUBLIC_KEY_HERE",
                amount="10.50",
                memo="Payment for services"
            )
            ```
        """
        return await self.payment_manager.send_payment(
            source_secret=source_secret,
            destination_public_key=destination_public_key,
            amount=amount,
            memo=memo
        )
    
    async def get_balance(self, public_key: str) -> float:
        """
        Get  balance for an account
        
        Args:
            public_key: Public key of the account
            
        Returns:
             balance as float
            
        Example:
            ```python
            client = SofizPayClient()
            balance = await client.get_balance("PUBLIC_KEY_HERE")
            ```
        """
        return await self.payment_manager.get_balance(public_key)
    
    
    async def get_all_transactions(
        self,
        public_key: str,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Get all transactions (not just ) for an account
        
        Args:
            public_key: Public key of the account
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of all transaction dictionaries
            
        Example:
            ```python
            client = SofizPayClient()
            transactions = await client.get_all_transactions("PUBLIC_KEY_HERE", limit=50)
            for tx in transactions:
            ```
        """
        return await self.transaction_manager.get_all_transactions(public_key, limit)
    
    def get_public_key_from_secret(self, secret_key: str) -> str:
        """
        Extract public key from secret key
        
        Args:
            secret_key: The secret key
            
        Returns:
            The corresponding public key
            
        Example:
            ```python
            client = SofizPayClient()
            public_key = client.get_public_key_from_secret("SECRET_KEY_HERE")
            ```
        """
        return self.payment_manager.get_public_key_from_secret(secret_key)
    
    async def get_transactions(
        self,
        public_key: str,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Get  transactions for an account
        
        Args:
            public_key: Public key of the account
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of  transaction dictionaries
            
        Example:
            ```python
            client = SofizPayClient()
            transactions = await client.get_transactions("PUBLIC_KEY_HERE", limit=50)
            for tx in transactions:
            ```
        """
        return await self.transaction_manager.get_transactions(public_key, limit)
    
    async def get_transaction_by_hash(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Get detailed transaction information by hash
        
        Args:
            transaction_hash: Hash of the transaction to retrieve
            
        Returns:
            Detailed transaction information
            
        Example:
            ```python
            client = SofizPayClient()
            result = await client.get_transaction_by_hash("TRANSACTION_HASH_HERE")
            if result['found']:
                tx = result['transaction']
            ```
        """
        return await self.transaction_manager.get_transaction_by_hash(transaction_hash)
    
    async def setup_transaction_stream(
        self,
        public_key: str,
        transaction_callback: Callable[[Dict[str, Any]], None],
        from_now: bool = True,
        check_interval: int = 30
    ) -> str:
        """
        Set up real-time transaction streaming for an account 
        
        Args:
            public_key: Public key to monitor
            transaction_callback: Callback function to handle new transactions
            from_now: If True, only new transactions will be streamed; if False, both new and historical transactions will be included
            check_interval: Duration in seconds for repeated network checks (default 30 seconds)
            
        Returns:
            Stream ID for managing the stream
            
        Example:
            ```python
            client = SofizPayClient()
            
            def handle_transaction(transaction):
                print("New transaction:", transaction)
            

            stream_id = await client.setup_transaction_stream(
                "PUBLIC_KEY_HERE",
                handle_transaction,
                from_now=True,
                check_interval=10
            )
            
            stream_id = await client.setup_transaction_stream(
                "PUBLIC_KEY_HERE", 
                handle_transaction,
                from_now=False,
                check_interval=60
            )
            ```
        """
        return await self.transaction_manager.setup_transaction_stream(
            public_key, transaction_callback, from_now=from_now, check_interval=check_interval  
        )
    
    def stop_transaction_stream(self, stream_id: str) -> bool:
        """
        Stop a transaction stream
        
        Args:
            stream_id: ID of the stream to stop
            
        Returns:
            True if stream was stopped, False if not found
            
        Example:
            ```python
            client = SofizPayClient()
            success = client.stop_transaction_stream(stream_id)
            if success:
            ```
        """
        return self.transaction_manager.stop_transaction_stream(stream_id)
    
    @classmethod
    def verify_signature(cls, message: str, signature: str) -> bool:
        """
        Verify a signature against a message using SofizPay's official public key
        
        Args:
            message: The original message
            signature: The signature to verify
            
        Returns:
            True if signature is valid, False otherwise
            
        Example:
            ```python
            client = SofizPayClient()
            is_valid = client.verify_signature(
                message="Hello, world!",
                signature="SIGNATURE_HERE"
            )
            ```
        """
        try:
            decoded_signature = base64.b64decode(signature)
            
            public_key_obj = serialization.load_pem_public_key(cls.SOFIZPAY_PUBLIC_KEY_PEM.encode())
            
            public_key_obj.verify(
                decoded_signature,
                message.encode(),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            return True
        except (InvalidSignature, ValueError, TypeError) as e:
            return False
    
    async def make_cib_transaction(self, transaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make a CIB transaction through SofizPay
        
        Args:
            transaction_data: Dictionary containing transaction details:
                - account (str): Required. Account identifier
                - amount (float): Required. Transaction amount (must be > 0)
                - full_name (str): Required. Customer full name
                - phone (str): Required. Customer phone number
                - email (str): Required. Customer email address
                - return_url (str, optional): URL to redirect after transaction
                - memo (str, optional): Optional memo for the transaction
                - redirect (bool, optional): Whether to redirect (defaults to False)
                
        Returns:
            Dictionary with transaction result
            
        Raises:
            ValidationError: When required fields are missing or invalid
            NetworkError: When request fails
            
        Example:
            ```python
            client = SofizPayClient()
            result = await client.make_cib_transaction({
                "account": "ACCOUNT_ID_HERE",
                "amount": 100.50,
                "full_name": "CLIENT",
                "phone": "+213123456789",
                "email": "CLIENT@example.com",
                "memo": "Payment for services",
                "return_url": "https://mysite.com/success"
            })
            
            if result['success']:
            ```
        """
        if not transaction_data.get('account'):
            raise ValidationError('Account is required')
        
        if not transaction_data.get('amount') or float(transaction_data['amount']) <= 0:
            raise ValidationError('Valid amount is required')
        
        if not transaction_data.get('full_name'):
            raise ValidationError('Full name is required')
        
        if not transaction_data.get('phone'):
            raise ValidationError('Phone number is required')
        
        if not transaction_data.get('email'):
            raise ValidationError('Email is required')
        
        try:
            base_url = 'https://www.sofizpay.com/make-cib-transaction/'
            
            query_params = []
            query_params.append(f"account={urllib.parse.quote(str(transaction_data['account']))}")
            query_params.append(f"amount={transaction_data['amount']}")
            query_params.append(f"full_name={urllib.parse.quote(transaction_data['full_name'])}")
            query_params.append(f"phone={urllib.parse.quote(transaction_data['phone'])}")
            query_params.append(f"email={urllib.parse.quote(transaction_data['email'])}")
            
            # Add optional parameters
            if transaction_data.get('return_url'):
                query_params.append(f"return_url={urllib.parse.quote(transaction_data['return_url'])}")
            
            if transaction_data.get('memo'):
                safe_memo = urllib.parse.quote(transaction_data['memo'])
                query_params.append(f"memo={safe_memo}")
            
            query_params.append("redirect=no")
            
            full_url = f"{base_url}?{'&'.join(query_params)}"
            
            
            response = requests.get(
                full_url,
                headers={
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                    'User-Agent': f'SofizPay-Python-SDK/{self.VERSION}'
                },
                timeout=30
            )
            
            response.raise_for_status()
            
            return {
                'success': True,
                'data': response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text,
                'status': response.status_code,
                'status_text': response.reason,
                'headers': dict(response.headers),
                'url': full_url,
                'request_data': {
                    'account': transaction_data['account'],
                    'amount': transaction_data['amount'],
                    'full_name': transaction_data['full_name'],
                    'phone': transaction_data['phone'],
                    'email': transaction_data['email'],
                    'return_url': transaction_data.get('return_url'),
                    'memo': transaction_data.get('memo'),
                    'redirect': 'no'
                },
                'timestamp': datetime.now().isoformat()
            }
            
        except requests.exceptions.HTTPError as e:
            error_message = f"HTTP Error: {e.response.status_code} - {e.response.reason}"
            
            try:
                error_data = e.response.json()
                if 'error' in error_data:
                    error_message += f" - {error_data['error']}"
            except:
                pass
            
            return {
                'success': False,
                'error': error_message,
                'account': transaction_data['account'],
                'amount': transaction_data['amount'],
                'timestamp': datetime.now().isoformat(),
                'status_code': e.response.status_code
            }
            
        except requests.exceptions.RequestException as e:
            error_message = f"Request error: {str(e)}"
            
            if isinstance(e, requests.exceptions.Timeout):
                error_message = "Request timeout: Server took too long to respond"
            elif isinstance(e, requests.exceptions.ConnectionError):
                error_message = "Network error: Could not connect to server"
            
            return {
                'success': False,
                'error': error_message,
                'account': transaction_data['account'],
                'amount': transaction_data['amount'],
                'timestamp': datetime.now().isoformat()
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': f"Unexpected error: {str(e)}",
                'account': transaction_data['account'],
                'amount': transaction_data['amount'],
                'timestamp': datetime.now().isoformat()
            }
    
    def verify_sofizpay_signature(self, verification_data: Dict[str, str]) -> bool:
        """
        Verify a signature from SofizPay using the official public key
        
        Args:
            verification_data: Dictionary containing:
                - message (str): The original message that was signed
                - signature_url_safe (str): The URL-safe base64 encoded signature
                
        Returns:
            True if signature is valid, False otherwise
            

            ```
        """
        if not verification_data.get('message'):
            return False
        
        if not verification_data.get('signature_url_safe'):
            return False
        
        try:
            signature_url_safe = verification_data['signature_url_safe']
            base64_signature = signature_url_safe.replace('-', '+').replace('_', '/')
            
            while len(base64_signature) % 4:
                base64_signature += '='
            
            signature_bytes = base64.b64decode(base64_signature)
            
            public_key = serialization.load_pem_public_key(
                self.SOFIZPAY_PUBLIC_KEY_PEM.encode()
            )
            
            public_key.verify(
                signature_bytes,
                verification_data['message'].encode('utf-8'),
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            return True
            
        except InvalidSignature:
            return False
        except Exception as e:
            return False

    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit - cleanup resources"""
        for stream_id in list(self.transaction_manager._streaming_tasks.keys()):
            self.stop_transaction_stream(stream_id)
