"""Test suite for SofizPay SDK"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from stellar_sdk import Keypair

from sofizpay import SofizPayClient, PaymentError, ValidationError, NetworkError
from sofizpay.utils import validate_public_key, validate_secret_key, validate_amount, get_public_key_from_secret


class TestSofizPayClient:
    """Test cases for SofizPayClient"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = SofizPayClient()
        self.test_keypair = Keypair.random()
        self.test_public_key = self.test_keypair.public_key
        self.test_secret_key = self.test_keypair.secret
        
    def test_client_initialization(self):
        """Test client initialization"""
        client = SofizPayClient()
        assert client.server_url == "https://horizon.stellar.org"
        
        custom_client = SofizPayClient("https://horizon-testnet.stellar.org")
        assert custom_client.server_url == "https://horizon-testnet.stellar.org"
    
    def test_validate_public_key(self):
        """Test public key validation"""
        # Valid public key
        assert validate_public_key(self.test_public_key) is True
        
        # Invalid public keys
        assert validate_public_key("invalid_key") is False
        assert validate_public_key("") is False
        assert validate_public_key(None) is False
    
    def test_validate_secret_key(self):
        """Test secret key validation"""
        # Valid secret key
        assert validate_secret_key(self.test_secret_key) is True
        
        # Invalid secret keys
        assert validate_secret_key("invalid_key") is False
        assert validate_secret_key("") is False
        assert validate_secret_key(None) is False
    
    def test_get_public_key_from_secret(self):
        """Test extracting public key from secret"""
        extracted_public = self.client.get_public_key_from_secret(self.test_secret_key)
        assert extracted_public == self.test_public_key
        
        # Test with invalid secret
        with pytest.raises(ValidationError):
            self.client.get_public_key_from_secret("invalid_secret")
    
    def test_validate_amount(self):
        """Test amount validation"""
        # Valid amounts
        assert validate_amount("10.50") is True
        assert validate_amount("0.0000001") is True
        assert validate_amount("1000000") is True
        
        # Invalid amounts
        assert validate_amount("0") is False
        assert validate_amount("-10") is False
        assert validate_amount("invalid") is False
        assert validate_amount("") is False


class TestPaymentOperations:
    """Test cases for payment operations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = SofizPayClient()
        self.source_keypair = Keypair.random()
        self.dest_keypair = Keypair.random()
    
    @pytest.mark.asyncio
    async def test_send_payment_validation(self):
        """Test payment input validation"""
        with pytest.raises(ValidationError):
            await self.client.send_payment(
                source_secret="invalid_secret",
                destination_public_key=self.dest_keypair.public_key,
                amount="10.50"
            )
        
        with pytest.raises(ValidationError):
            await self.client.send_payment(
                source_secret=self.source_keypair.secret,
                destination_public_key="invalid_public_key",
                amount="10.50"
            )
        
        with pytest.raises(ValidationError):
            await self.client.send_payment(
                source_secret=self.source_keypair.secret,
                destination_public_key=self.dest_keypair.public_key,
                amount="invalid_amount"
            )
    
    @pytest.mark.asyncio
    @patch('sofizpay.payments.PaymentManager.send_payment')
    async def test_send_payment_success(self, mock_send_payment):
        """Test successful payment"""
        mock_send_payment.return_value = {
            'success': True,
            'hash': 'test_hash_123',
            'duration': 2.5,
            'ledger': 12345
        }
        
        result = await self.client.send_payment(
            source_secret=self.source_keypair.secret,
            destination_public_key=self.dest_keypair.public_key,
            amount="10.50",
            memo="Test payment"
        )
        
        assert result['success'] is True
        assert result['hash'] == 'test_hash_123'
        assert result['duration'] == 2.5
        mock_send_payment.assert_called_once()


class TestTransactionOperations:
    """Test cases for transaction operations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = SofizPayClient()
        self.test_keypair = Keypair.random()
    
    @pytest.mark.asyncio
    @patch('sofizpay.transactions.TransactionManager.get_dzt_transactions')
    async def test_get_dzt_transactions(self, mock_get_transactions):
        """Test getting DZT transactions"""
        mock_transactions = [
            {
                'id': 'tx1',
                'hash': 'hash1',
                'amount': '10.50',
                'type': 'received',
                'asset_code': 'DZT'
            },
            {
                'id': 'tx2', 
                'hash': 'hash2',
                'amount': '5.25',
                'type': 'sent',
                'asset_code': 'DZT'
            }
        ]
        mock_get_transactions.return_value = mock_transactions
        
        transactions = await self.client.get_dzt_transactions(
            self.test_keypair.public_key,
            limit=10
        )
        
        assert len(transactions) == 2
        assert transactions[0]['amount'] == '10.50'
        assert transactions[1]['type'] == 'sent'
        mock_get_transactions.assert_called_once_with(self.test_keypair.public_key, 10)
    
    @pytest.mark.asyncio
    @patch('sofizpay.transactions.TransactionManager.get_transaction_by_hash')
    async def test_get_transaction_by_hash_found(self, mock_get_transaction):
        """Test getting transaction by hash - found"""
        mock_transaction_data = {
            'success': True,
            'found': True,
            'transaction': {
                'hash': 'test_hash',
                'amount': '15.75',
                'successful': True
            },
            'dzt_operations_count': 1
        }
        mock_get_transaction.return_value = mock_transaction_data
        
        result = await self.client.get_transaction_by_hash('test_hash')
        
        assert result['success'] is True
        assert result['found'] is True
        assert result['transaction']['amount'] == '15.75'
        mock_get_transaction.assert_called_once_with('test_hash')
    
    @pytest.mark.asyncio
    @patch('sofizpay.transactions.TransactionManager.get_transaction_by_hash')
    async def test_get_transaction_by_hash_not_found(self, mock_get_transaction):
        """Test getting transaction by hash - not found"""
        mock_get_transaction.return_value = {
            'success': False,
            'found': False,
            'message': 'Transaction not found',
            'hash': 'nonexistent_hash'
        }
        
        result = await self.client.get_transaction_by_hash('nonexistent_hash')
        
        assert result['success'] is False
        assert result['found'] is False
        assert 'not found' in result['message']


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_validate_public_key(self):
        """Test public key validation utility"""
        test_keypair = Keypair.random()
        
        # Valid key
        assert validate_public_key(test_keypair.public_key) is True
        
        # Invalid keys
        assert validate_public_key("invalid") is False
        assert validate_public_key("") is False
        assert validate_public_key(None) is False
    
    def test_validate_secret_key(self):
        """Test secret key validation utility"""
        test_keypair = Keypair.random()
        
        # Valid key
        assert validate_secret_key(test_keypair.secret) is True
        
        # Invalid keys
        assert validate_secret_key("invalid") is False
        assert validate_secret_key("") is False
        assert validate_secret_key(None) is False
    
    def test_get_public_key_from_secret_utility(self):
        """Test public key extraction utility"""
        test_keypair = Keypair.random()
        
        extracted_public = get_public_key_from_secret(test_keypair.secret)
        assert extracted_public == test_keypair.public_key
        
        # Test with invalid secret
        with pytest.raises(ValidationError):
            get_public_key_from_secret("invalid_secret")


class TestStreamingOperations:
    """Test cases for transaction streaming"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = SofizPayClient()
        self.test_keypair = Keypair.random()
    
    @pytest.mark.asyncio
    @patch('sofizpay.transactions.TransactionManager.setup_transaction_stream')
    async def test_setup_transaction_stream(self, mock_setup_stream):
        """Test setting up transaction stream"""
        mock_setup_stream.return_value = "stream_123"
        
        def dummy_callback(transaction):
            pass
        
        stream_id = await self.client.setup_transaction_stream(
            self.test_keypair.public_key,
            dummy_callback
        )
        
        assert stream_id == "stream_123"
        mock_setup_stream.assert_called_once_with(self.test_keypair.public_key, dummy_callback, cursor='now')
    
    @patch('sofizpay.transactions.TransactionManager.stop_transaction_stream')
    def test_stop_transaction_stream(self, mock_stop_stream):
        """Test stopping transaction stream"""
        mock_stop_stream.return_value = True
        
        result = self.client.stop_transaction_stream("stream_123")
        
        assert result is True
        mock_stop_stream.assert_called_once_with("stream_123")


@pytest.mark.asyncio
async def test_context_manager():
    """Test async context manager functionality"""
    async with SofizPayClient() as client:
        assert isinstance(client, SofizPayClient)
        assert client.server_url == "https://horizon.stellar.org"


if __name__ == "__main__":
    pytest.main([__file__])
