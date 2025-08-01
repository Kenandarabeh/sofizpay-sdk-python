"""Payment management for SofizPay SDK"""

import time
from typing import Optional, Dict, Any
from stellar_sdk import (
    Server, Keypair, Asset, TransactionBuilder, 
    Network, Memo
)
from stellar_sdk.operation import Payment
from stellar_sdk.exceptions import SdkError

from .exceptions import PaymentError, ValidationError, NetworkError
from .utils import (
    validate_public_key, validate_secret_key, get_public_key_from_secret,
    validate_amount, validate_memo
)


class PaymentManager:
    """Manages payment operations using Stellar network"""
    
    ASSET_CODE = "DZT"
    ASSET_ISSUER = "GCAZI7YBLIDJWIVEL7ETNAZGPP3LC24NO6KAOBWZHUERXQ7M5BC52DLV"
    
    def __init__(self, server_url: str = "https://horizon.stellar.org"):
        """
        Initialize PaymentManager
        
        Args:
            server_url: Stellar Horizon server URL
        """
        self.server = Server(horizon_url=server_url)
        self.network_passphrase = Network.PUBLIC_NETWORK_PASSPHRASE
    
    async def send_payment(
        self,
        source_secret: str,
        destination_public_key: str,
        amount: str,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send a payment on the Stellar network
        
        Args:
            source_secret: Secret key of the source account
            destination_public_key: Public key of the destination account
            amount: Amount to send
            memo: Optional memo to attach to transaction
            
        Returns:
            Dictionary with transaction result
            
        Raises:
            PaymentError: When payment fails
            ValidationError: When input validation fails
        """
        start_time = time.time()
        
        try:
            asset_code = self.ASSET_CODE
            asset_issuer = self.ASSET_ISSUER
            
            if not validate_secret_key(source_secret):
                raise ValidationError("Invalid source secret key")
            
            if not validate_public_key(destination_public_key):
                raise ValidationError("Invalid destination public key")
            
            if not validate_amount(amount):
                raise ValidationError("Invalid amount")
            
            source_keypair = Keypair.from_secret(source_secret)
            source_public_key = source_keypair.public_key
            
            asset = Asset(asset_code, asset_issuer)
            
            try:
                source_account = self.server.load_account(source_public_key)
            except Exception as e:
                raise PaymentError(f"Failed to load source account: {e}")
            
            transaction_builder = TransactionBuilder(
                source_account=source_account,
                network_passphrase=self.network_passphrase,
                base_fee=200  
            )
            
            payment_operation = Payment(
                destination=destination_public_key,
                asset=asset,
                amount=str(amount)
            )
            transaction_builder.append_operation(payment_operation)
            
            if memo:
                is_valid, processed_memo = validate_memo(memo)
                if is_valid and processed_memo:
                    transaction_builder.add_text_memo(processed_memo)
            
            transaction_builder.set_timeout(60)
            transaction = transaction_builder.build()
            
            transaction.sign(source_keypair)
            
            try:
                response = self.server.submit_transaction(transaction)
                
                return response  # إرجاع النتيجة مباشرة
                
            except SdkError as e:
                raise PaymentError(f"Transaction submission failed: {e}")
                
        except (ValidationError, PaymentError):
            raise
        except Exception as e:
            detailed_error = self._extract_error_details(e)
            raise PaymentError(detailed_error)
    
    def _extract_error_details(self, error: Exception) -> str:
        """Extract detailed error information from Stellar SDK error"""
        detailed_error = str(error)
        
        if hasattr(error, 'response') and error.response:
            if hasattr(error.response, 'json'):
                try:
                    error_data = error.response.json()
                    
                    if 'extras' in error_data:
                        extras = error_data['extras']
                        
                        if 'result_codes' in extras:
                            codes = extras['result_codes']
                            if 'transaction' in codes:
                                detailed_error = f"Transaction error: {codes['transaction']}"
                            if 'operations' in codes and codes['operations']:
                                detailed_error += f" | Operation errors: {', '.join(codes['operations'])}"
                        
                        if 'envelope_xdr' in extras:
                            pass
                        if 'result_xdr' in extras:
                            pass
                            
                except Exception:
                    pass
        
        return detailed_error
    
    async def get_balance(self, public_key: str) -> float:
        """
        Get  balance for an account
        
        Args:
            public_key: Public key of the account
            
        Returns:
             balance as float
            
        Raises:
            ValidationError: When public key is invalid
            NetworkError: When unable to fetch account data
        """
        if not validate_public_key(public_key):
            raise ValidationError("Invalid public key")
        
        try:
            account_details = self.server.accounts().account_id(public_key).call()
            
            for balance in account_details['balances']:
                if (balance.get('asset_code') == self.ASSET_CODE and
                    balance.get('asset_issuer') == self.ASSET_ISSUER):
                    return float(balance['balance'])
            
            return 0.0  
            
        except Exception as e:
            raise NetworkError(f"Error fetching  balance: {e}")
    
    def get_public_key_from_secret(self, secret_key: str) -> str:
        """
        Extract public key from secret key
        
        Args:
            secret_key: The secret key
            
        Returns:
            The corresponding public key
            
        Raises:
            ValidationError: If secret key is invalid
        """
        return get_public_key_from_secret(secret_key)
