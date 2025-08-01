"""Transaction management and streaming for SofizPay SDK"""

import asyncio
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Callable
from stellar_sdk import Server
from stellar_sdk.exceptions import SdkError

from .exceptions import TransactionError, ValidationError, NetworkError
from .utils import validate_public_key, fetch_with_retry, RateLimiter


class TransactionManager:
    """Manages transaction operations and streaming"""
    
    ASSET_CODE = "DZT"
    ASSET_ISSUER = "GCAZI7YBLIDJWIVEL7ETNAZGPP3LC24NO6KAOBWZHUERXQ7M5BC52DLV"
    
    def __init__(self, server_url: str = "https://horizon.stellar.org"):
        """
        Initialize TransactionManager
        Args:
            server_url: Stellar Horizon server URL
        """
        self.server = Server(horizon_url=server_url)
        self.rate_limiter = RateLimiter(max_calls=10, time_window=1)
        self._streaming_tasks = {}
    
    async def setup_transaction_stream(
        self,
        public_key: str,
        transaction_callback: Callable[[Dict[str, Any]], None],
        from_now: bool = True,
        check_interval: int = 30
    ) -> str:
        """
        Set up real-time transaction streaming for an account (يعمل مثل JavaScript تماماً)
        
        Args:
            public_key: Public key to monitor
            transaction_callback: Callback function to handle new transactions
            from_now: If True, only new transactions after stream start are sent, If False, both new and historical transactions are sent
            check_interval: Duration in seconds for repeated network checks (default 30 seconds)
            
        Returns:
            Stream ID for managing the stream
        """
        if not validate_public_key(public_key):
            raise ValidationError("Invalid public key")
        
        if check_interval < 5 :
            raise ValidationError("Check interval must be more then 5 seconds")
        
        stream_id = f"stream_{public_key}_{id(transaction_callback)}"
        
        from datetime import datetime, timezone
        stream_start_time = datetime.now(timezone.utc)
        
        if not from_now:
            try:
                previous_transactions = await self.get_transactions(public_key, 200) 
                
                if previous_transactions:
                    for tx in reversed(previous_transactions): 
                        formatted_transaction = {
                            'id': tx.get('hash') or tx.get('id'),
                            'transactionId': tx.get('hash') or tx.get('id'),
                            'hash': tx.get('hash') or tx.get('id'),
                            'amount': float(tx.get('amount', 0)),
                            'memo': tx.get('memo', ''),
                            'type': tx.get('type', 'unknown'),
                            'from': tx.get('from', ''),
                            'to': tx.get('to', ''),
                            'asset_code': tx.get('asset_code', ''),
                            'asset_issuer': tx.get('asset_issuer', ''),
                            'status': 'completed',
                            'timestamp': tx.get('created_at'),
                            'created_at': tx.get('created_at'),
                            'processed_at': tx.get('created_at'),
                            'isHistorical': True 
                        }
                        
                        try:
                            if asyncio.iscoroutinefunction(transaction_callback):
                                await transaction_callback(formatted_transaction)
                            else:
                                transaction_callback(formatted_transaction)
                            await asyncio.sleep(0.05) 
                        except Exception as e:
                            print(f"Error in historical callback: {e}")
                    
                    history_complete = {
                        'id': 'HISTORY_COMPLETE',
                        'isHistoryComplete': True,
                        'historicalCount': len(previous_transactions),
                        'message': f'{len(previous_transactions)} historical transactions loaded, now listening for new transactions...'
                    }
                    
                    try:
                        if asyncio.iscoroutinefunction(transaction_callback):
                            await transaction_callback(history_complete)
                        else:
                            transaction_callback(history_complete)
                    except Exception as e:
                        print(f"Error in history complete callback: {e}")
                        
            except Exception as error:
                print(f'{error}')
        
        async def tx_handler(tx_response):

            try:
                if from_now:
                    transaction_time_str = tx_response.get('created_at', '')
                    if transaction_time_str:
                        try:
                            transaction_time = datetime.fromisoformat(transaction_time_str.replace('Z', '+00:00'))
                            if transaction_time <= stream_start_time:
                                return
                        except Exception as date_error:
                            print(f"{date_error}")
                            return
                
                transaction_url = f"{self.server.horizon_url}/transactions/{tx_response.get('id')}"
                transaction_data = await fetch_with_retry(transaction_url)
                memo = transaction_data.get('memo', '')
                
                operations_url = f"{self.server.horizon_url}/transactions/{transaction_data.get('id')}/operations"
                operations_data = await fetch_with_retry(operations_url)
                
                operations = [
                    op for op in operations_data.get('_embedded', {}).get('records', [])
                    if (op.get('asset_code') == self.ASSET_CODE and 
                        op.get('asset_issuer') == self.ASSET_ISSUER and 
                        op.get('amount'))
                ]
                
                for operation in operations:
                    transaction_type = 'sent' if operation.get('from') == public_key else 'received'
                    
                    new_transaction = {
                        'id': transaction_data.get('hash'),
                        'transactionId': transaction_data.get('hash'),
                        'hash': transaction_data.get('hash'),
                        'amount': float(operation.get('amount', 0)),
                        'memo': memo,
                        'type': transaction_type,
                        'from': operation.get('from', ''),
                        'to': operation.get('to') or operation.get('destination', ''),
                        'asset_code': operation.get('asset_code', ''),
                        'asset_issuer': operation.get('asset_issuer', ''),
                        'status': 'completed',
                        'timestamp': transaction_data.get('created_at'),
                        'created_at': transaction_data.get('created_at'),
                        'processed_at': datetime.now().isoformat(),
                        'isHistorical': False 
                    }
                    
                    try:
                        if asyncio.iscoroutinefunction(transaction_callback):
                            await transaction_callback(new_transaction)
                        else:
                            transaction_callback(new_transaction)
                    except Exception as e:
                        print(f"Error in callback: {e}")
                        
            except Exception as error:
                print(f'Error fetching transaction details: {error}')
        
        async def start_stream():
            try:
                while stream_id in self._streaming_tasks:
                    try:
                        stream_builder = (self.server.transactions()
                                        .for_account(public_key)
                                        .cursor('now')
                                        .order('desc')
                                        .limit(10))
                        
                        response = stream_builder.call()
                        
                        for transaction in response.get('_embedded', {}).get('records', []):
                            await tx_handler(transaction)
                        
                        await asyncio.sleep(check_interval)
                        
                    except Exception as error:
                        print(f'Error in transaction stream: {error}')
                        
                        await asyncio.sleep(check_interval)
                        
            except asyncio.CancelledError:
                print(f'Stream {stream_id} cancelled')
            except Exception as error:
                print(f'Error starting transaction stream: {error}')
                await asyncio.sleep(check_interval)
                await start_stream()
        
        task = asyncio.create_task(start_stream())
        self._streaming_tasks[stream_id] = task
        
        return stream_id
    
    def stop_transaction_stream(self, stream_id: str) -> bool:
        """
        Stop a transaction stream
        
        Args:
            stream_id: ID of the stream to stop
            
        Returns:
            True if stream was stopped, False if not found
        """
        if stream_id in self._streaming_tasks:
            self._streaming_tasks[stream_id].cancel()
            del self._streaming_tasks[stream_id]
            return True
        return False
    
    async def get_all_transactions(
        self,
        public_key: str,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Get  transactions for an account (filtering only  operations)
        
        Args:
            public_key: Public key of the account
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of  transaction dictionaries
            
        Raises:
            ValidationError: When public key is invalid
            NetworkError: When unable to fetch transactions
        """
        if not validate_public_key(public_key):
            raise ValidationError("Invalid public key")
        try:
            transactions_response = (self.server.transactions()
                                   .for_account(public_key)
                                   .order('desc')
                                   .limit(limit)
                                   .call())
            return transactions_response.get('_embedded', {}).get('records', []) 
        except Exception as e:
            raise NetworkError(f"Error fetching transactions: {e}")

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
            
        Raises:
            ValidationError: When public key is invalid
            NetworkError: When unable to fetch transactions
        """
        if not validate_public_key(public_key):
            raise ValidationError("Invalid public key")
        
        try:
            transactions_response = (self.server.transactions()
                                   .for_account(public_key)
                                   .order('desc')
                                   .limit(limit)
                                   .call())
            
            dzt_transactions = []
            
            for tx in transactions_response.get('_embedded', {}).get('records', []):
                try:
                    operations_response = (self.server.operations()
                                         .for_transaction(tx['id'])
                                         .call())
                    
                    for op in operations_response.get('_embedded', {}).get('records', []):
                        if (op.get('type') == 'payment' and
                            op.get('asset_code') == self.ASSET_CODE and
                            op.get('asset_issuer') == self.ASSET_ISSUER):
                            
                            transaction_type = 'sent' if op.get('from') == public_key else 'received'
                            
                            dzt_transactions.append({
                                'id': tx['id'],
                                'hash': tx['hash'],
                                'created_at': tx['created_at'],
                                'memo': tx.get('memo', ''),
                                'amount': op.get('amount'),
                                'from': op.get('from'),
                                'to': op.get('to'),
                                'type': transaction_type,
                                'asset_code': op.get('asset_code'),
                                'asset_issuer': op.get('asset_issuer'),
                                'successful': tx.get('successful', False)
                            })
                            
                except Exception as op_error:
                    continue
            
            return dzt_transactions
            
        except Exception as e:
            raise NetworkError(f"Error fetching  transactions: {e}")
    
    async def get_transaction_by_hash(self, transaction_hash: str) -> Dict[str, Any]:
        """
        Get detailed transaction information by hash
        
        Args:
            transaction_hash: Hash of the transaction to retrieve
            
        Returns:
            Detailed transaction information
            
        Raises:
            TransactionError: When transaction is not found or error occurs
        """
        if not transaction_hash:
            raise TransactionError("Transaction hash is required")
        try:
            transaction_data = self.server.transactions().transaction(transaction_hash).call()
            return transaction_data  # إرجاع بيانات المعاملة مباشرة
        except SdkError as e:
            if "404" in str(e):
                return {}
            else:
                raise TransactionError(f"Error fetching transaction: {e}")
        except Exception as e:
            return {}
    
    def __del__(self):
        """Cleanup streaming tasks when object is destroyed"""
        for stream_id in list(self._streaming_tasks.keys()):
            self.stop_transaction_stream(stream_id)
