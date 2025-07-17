"""Transaction management and streaming for SofizPay SDK"""

import asyncio
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
        cursor: str = 'now'
    ) -> str:
        """
        Set up real-time transaction streaming for an account (only NEW transactions)
        
        Args:
            public_key: Public key to monitor
            transaction_callback: Callback function to handle new transactions
            cursor: Starting point for streaming ('now' for only new transactions)
            
        Returns:
            Stream ID for managing the stream
            
        Raises:
            ValidationError: When public key is invalid
        """
        if not validate_public_key(public_key):
            raise ValidationError("Invalid public key")
        
        stream_id = f"stream_{public_key}_{id(transaction_callback)}"
        
        from datetime import datetime, timezone
        stream_start_time = datetime.now(timezone.utc)
        
        try:
            latest_tx_response = (self.server.transactions()
                                .for_account(public_key)
                                .order('desc')
                                .limit(1)
                                .call())
            
            latest_transactions = latest_tx_response.get('_embedded', {}).get('records', [])
            if latest_transactions:
                latest_cursor = latest_transactions[0].get('paging_token')
            else:
                latest_cursor = 'now'
        except Exception as e:
            latest_cursor = 'now'
        
        async def transaction_handler(response):
            """Handle incoming transaction data - only DZT transactions AFTER stream start"""
            try:
                await self.rate_limiter.acquire()
                
                transaction_time_str = response.get('created_at', '')
                if transaction_time_str:
                    from datetime import datetime, timezone
                    try:
                        transaction_time = datetime.fromisoformat(transaction_time_str.replace('Z', '+00:00'))
                        if transaction_time <= stream_start_time:
                            return
                        else:
                            pass
                    except Exception as date_error:
                        return
                
                transaction_url = f"{self.server.horizon_url}/transactions/{response['id']}"
                transaction_data = await fetch_with_retry(transaction_url)
                
                memo = transaction_data.get('memo', '')
                
                operations_url = f"{self.server.horizon_url}/transactions/{response['id']}/operations"
                operations_data = await fetch_with_retry(operations_url)
                
                dzt_operations = [
                    op for op in operations_data.get('_embedded', {}).get('records', [])
                    if (op.get('type') == 'payment' and 
                        op.get('asset_code') == self.ASSET_CODE and 
                        op.get('asset_issuer') == self.ASSET_ISSUER and 
                        op.get('amount'))
                ]
                
                for operation in dzt_operations:
                    transaction_type = 'sent' if operation.get('from') == public_key else 'received'
                    
                    new_transaction = {
                        'id': transaction_data.get('hash'),
                        'memo': memo,
                        'amount': operation.get('amount', ''),
                        'status': 'confirmed' if transaction_data.get('successful') else 'failed',
                        'source_account': operation.get('source_account', ''),
                        'from': operation.get('from', ''),
                        'to': operation.get('to') or operation.get('destination', ''),
                        'type': transaction_type,
                        'asset_code': operation.get('asset_code', ''),
                        'asset_issuer': operation.get('asset_issuer', ''),
                        'created_at': transaction_data.get('created_at', ''),
                        'processed_at': asyncio.get_event_loop().time(),
                        'successful': transaction_data.get('successful', False)
                    }
                    
                    
                    try:
                        if asyncio.iscoroutinefunction(transaction_callback):
                            await transaction_callback(new_transaction)
                        else:
                            transaction_callback(new_transaction)
                    except Exception as e:
                        pass
            except Exception as e:
                pass
        
        async def error_handler(error):
            """Handle streaming errors"""
            pass
            if hasattr(error, 'status') and error.status == 429:
                await asyncio.sleep(60)
                await self.setup_transaction_stream(public_key, transaction_callback, latest_cursor)
        
        async def stream_task():
            """Main streaming task"""
            try:
                call_builder = self.server.transactions().for_account(public_key).cursor(latest_cursor)
                
                
                while stream_id in self._streaming_tasks:
                    try:
                        response = call_builder.limit(10).order('desc').call()
                        
                        for transaction in response.get('_embedded', {}).get('records', []):
                            await transaction_handler(transaction)
                        
                        await asyncio.sleep(5)  
                        
                    except Exception as e:
                        await error_handler(e)
                        await asyncio.sleep(10)  
                        
            except asyncio.CancelledError:
                pass
            except Exception as e:
                pass
        task = asyncio.create_task(stream_task())
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
        Get DZT transactions for an account (filtering only DZT operations)
        
        Args:
            public_key: Public key of the account
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of DZT transaction dictionaries
            
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
                    
                    has_dzt_operations = False
                    dzt_operations = []
                    
                    for op in operations_response.get('_embedded', {}).get('records', []):
                        if (op.get('type') == 'payment' and
                            op.get('asset_code') == self.ASSET_CODE and
                            op.get('asset_issuer') == self.ASSET_ISSUER):
                            
                            has_dzt_operations = True
                            transaction_type = 'sent' if op.get('from') == public_key else 'received'
                            
                            dzt_operation = {
                                'type': op.get('type'),
                                'amount': op.get('amount'),
                                'from': op.get('from'),
                                'to': op.get('to'),
                                'asset_code': op.get('asset_code'),
                                'asset_issuer': op.get('asset_issuer'),
                                'transaction_type': transaction_type
                            }
                            dzt_operations.append(dzt_operation)
                    
                    if has_dzt_operations:
                        formatted_transaction = {
                            'id': tx['id'],
                            'hash': tx['hash'],
                            'created_at': tx['created_at'],
                            'memo': tx.get('memo', ''),
                            'source_account': tx.get('source_account'),
                            'fee_charged': tx.get('fee_charged'),
                            'operation_count': tx.get('operation_count'),
                            'successful': tx.get('successful', False),
                            'dzt_operations': dzt_operations,
                            'dzt_operations_count': len(dzt_operations)
                        }
                        
                        if dzt_operations:
                            primary_op = dzt_operations[0]
                            formatted_transaction.update({
                                'amount': primary_op.get('amount'),
                                'from': primary_op.get('from'),
                                'to': primary_op.get('to'),
                                'type': primary_op.get('transaction_type'),
                                'asset_code': primary_op.get('asset_code'),
                                'asset_issuer': primary_op.get('asset_issuer')
                            })
                        
                        dzt_transactions.append(formatted_transaction)
                    
                except Exception as op_error:
                    continue
            
            return dzt_transactions
            
        except Exception as e:
            raise NetworkError(f"Error fetching DZT transactions: {e}")

    async def get_dzt_transactions(
        self,
        public_key: str,
        limit: int = 200
    ) -> List[Dict[str, Any]]:
        """
        Get DZT transactions for an account
        
        Args:
            public_key: Public key of the account
            limit: Maximum number of transactions to retrieve
            
        Returns:
            List of DZT transaction dictionaries
            
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
            raise NetworkError(f"Error fetching DZT transactions: {e}")
    
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
            
            try:
                transaction_data = self.server.transactions().transaction(transaction_hash).call()
            except SdkError as e:
                if "404" in str(e):
                    return {
                        'success': False,
                        'found': False,
                        'message': 'Transaction not found on Stellar network',
                        'hash': transaction_hash,
                        'error': 'Transaction does not exist'
                    }
                else:
                    raise TransactionError(f"Error fetching transaction: {e}")
            
            if not transaction_data:
                return {
                    'success': False,
                    'found': False,
                    'message': 'Transaction not found',
                    'hash': transaction_hash
                }
            
            try:
                operations_response = (self.server.operations()
                                     .for_transaction(transaction_hash)
                                     .call())
                operations = operations_response.get('_embedded', {}).get('records', [])
            except Exception as e:
                operations = []
            
            
            formatted_transaction = {
                'id': transaction_data.get('id'),
                'hash': transaction_data.get('hash'),
                'ledger': transaction_data.get('ledger'),
                'created_at': transaction_data.get('created_at'),
                'source_account': transaction_data.get('source_account'),
                'source_account_sequence': transaction_data.get('source_account_sequence'),
                'fee_charged': transaction_data.get('fee_charged'),
                'operation_count': transaction_data.get('operation_count'),
                'envelope_xdr': transaction_data.get('envelope_xdr'),
                'result_xdr': transaction_data.get('result_xdr'),
                'result_meta_xdr': transaction_data.get('result_meta_xdr'),
                'fee_meta_xdr': transaction_data.get('fee_meta_xdr'),
                'memo_type': transaction_data.get('memo_type'),
                'memo': transaction_data.get('memo', ''),
                'successful': transaction_data.get('successful'),
                'paging_token': transaction_data.get('paging_token'),
                'operations': []
            }
            
            payment_operations = []
            for op in operations:
                if op.get('type') == 'payment':
                    operation = {
                        'id': op.get('id'),
                        'type': op.get('type'),
                        'type_i': op.get('type_i'),
                        'created_at': op.get('created_at'),
                        'transaction_hash': op.get('transaction_hash'),
                        'source_account': op.get('source_account'),
                        'from': op.get('from'),
                        'to': op.get('to'),
                        'amount': op.get('amount'),
                        'asset_type': op.get('asset_type'),
                        'asset_code': op.get('asset_code'),
                        'asset_issuer': op.get('asset_issuer')
                    }
                    formatted_transaction['operations'].append(operation)
                    payment_operations.append(operation)
            
            dzt_operations = [
                op for op in payment_operations
                if (op.get('asset_code') == self.ASSET_CODE and
                    op.get('asset_issuer') == self.ASSET_ISSUER)
            ]
            
            if payment_operations:
                primary_op = payment_operations[0]
                formatted_transaction.update({
                    'amount': primary_op.get('amount'),
                    'from': primary_op.get('from'),
                    'to': primary_op.get('to'),
                    'asset_code': primary_op.get('asset_code'),
                    'asset_issuer': primary_op.get('asset_issuer'),
                    'operation_type': primary_op.get('type')
                })
            
            return {
                'success': True,
                'found': True,
                'transaction': formatted_transaction,
                'has_dzt_operations': len(dzt_operations) > 0,
                'dzt_operations_count': len(dzt_operations),
                'payment_operations_count': len(payment_operations),
                'dzt_operations': dzt_operations,
                'hash': transaction_hash,
                'message': f"Transaction found with {len(payment_operations)} payment operations ({len(dzt_operations)} DZT payments)"
            }
            
        except TransactionError:
            raise
        except Exception as e:
            return {
                'success': False,
                'found': False,
                'message': 'Error while searching for transaction',
                'hash': transaction_hash,
                'error': str(e)
            }
    
    def __del__(self):
        """Cleanup streaming tasks when object is destroyed"""
        for stream_id in list(self._streaming_tasks.keys()):
            self.stop_transaction_stream(stream_id)
