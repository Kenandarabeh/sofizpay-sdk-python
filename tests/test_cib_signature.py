"""Test cases for CIB transactions and signature verification"""

import pytest
from unittest.mock import Mock, patch
import requests

from sofizpay import SofizPayClient, ValidationError, NetworkError


class TestCIBTransactions:
    """Test cases for CIB transaction operations"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = SofizPayClient()
        self.valid_transaction_data = {
            "account": "test_account_123",
            "amount": 150.75,
            "full_name": "أحمد محمد علي",
            "phone": "+213123456789",
            "email": "ahmed@example.com",
            "memo": "دفع فاتورة اختبار",
            "return_url": "https://example.com/success"
        }
    
    @pytest.mark.asyncio
    async def test_make_cib_transaction_validation_missing_account(self):
        """Test CIB transaction validation - missing account"""
        transaction_data = self.valid_transaction_data.copy()
        del transaction_data['account']
        
        with pytest.raises(ValidationError, match="Account is required"):
            await self.client.make_cib_transaction(transaction_data)
    
    @pytest.mark.asyncio
    async def test_make_cib_transaction_validation_invalid_amount(self):
        """Test CIB transaction validation - invalid amount"""
        transaction_data = self.valid_transaction_data.copy()
        transaction_data['amount'] = -50
        
        with pytest.raises(ValidationError, match="Valid amount is required"):
            await self.client.make_cib_transaction(transaction_data)
    
    @pytest.mark.asyncio
    async def test_make_cib_transaction_validation_missing_fields(self):
        """Test CIB transaction validation - missing required fields"""
        required_fields = ['full_name', 'phone', 'email']
        
        for field in required_fields:
            transaction_data = self.valid_transaction_data.copy()
            del transaction_data[field]
            
            with pytest.raises(ValidationError):
                await self.client.make_cib_transaction(transaction_data)
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_make_cib_transaction_success(self, mock_get):
        """Test successful CIB transaction"""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.reason = "OK"
        mock_response.headers = {'content-type': 'application/json'}
        mock_response.json.return_value = {
            'transaction_id': 'tx_123456',
            'status': 'created',
            'payment_url': 'https://sofizpay.com/pay/tx_123456'
        }
        mock_get.return_value = mock_response
        
        result = await self.client.make_cib_transaction(self.valid_transaction_data)
        
        assert result['success'] is True
        assert result['status'] == 200
        assert result['status_text'] == "OK"
        assert 'data' in result
        assert result['data']['transaction_id'] == 'tx_123456'
        assert 'timestamp' in result
        assert 'request_data' in result
        
        # Verify the request was made with correct parameters
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert 'timeout' in call_args.kwargs
        assert call_args.kwargs['timeout'] == 30
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_make_cib_transaction_http_error(self, mock_get):
        """Test CIB transaction with HTTP error"""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.reason = "Bad Request"
        mock_response.json.return_value = {'error': 'Invalid account'}
        
        mock_get.side_effect = requests.exceptions.HTTPError(response=mock_response)
        mock_get.return_value.raise_for_status.side_effect = requests.exceptions.HTTPError(response=mock_response)
        
        result = await self.client.make_cib_transaction(self.valid_transaction_data)
        
        assert result['success'] is False
        assert 'HTTP Error' in result['error']
        assert result['account'] == self.valid_transaction_data['account']
        assert result['amount'] == self.valid_transaction_data['amount']
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_make_cib_transaction_timeout_error(self, mock_get):
        """Test CIB transaction with timeout error"""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        result = await self.client.make_cib_transaction(self.valid_transaction_data)
        
        assert result['success'] is False
        assert 'timeout' in result['error'].lower()
        assert result['account'] == self.valid_transaction_data['account']
    
    @pytest.mark.asyncio
    @patch('requests.get')
    async def test_make_cib_transaction_connection_error(self, mock_get):
        """Test CIB transaction with connection error"""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        result = await self.client.make_cib_transaction(self.valid_transaction_data)
        
        assert result['success'] is False
        assert 'network error' in result['error'].lower()
        assert result['account'] == self.valid_transaction_data['account']


class TestSignatureVerification:
    """Test cases for signature verification"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = SofizPayClient()
    
    def test_verify_sofizpay_signature_missing_message(self):
        """Test signature verification with missing message"""
        verification_data = {
            "signature_url_safe": "test_signature"
        }
        
        result = self.client.verify_sofizpay_signature(verification_data)
        assert result is False
    
    def test_verify_sofizpay_signature_missing_signature(self):
        """Test signature verification with missing signature"""
        verification_data = {
            "message": "test_message"
        }
        
        result = self.client.verify_sofizpay_signature(verification_data)
        assert result is False
    
    def test_verify_sofizpay_signature_invalid_signature_format(self):
        """Test signature verification with invalid signature format"""
        verification_data = {
            "message": "test_message",
            "signature_url_safe": "invalid_base64_!@#$%"
        }
        
        result = self.client.verify_sofizpay_signature(verification_data)
        assert result is False
    
    @patch('cryptography.hazmat.primitives.serialization.load_pem_public_key')
    def test_verify_sofizpay_signature_invalid_key(self, mock_load_key):
        """Test signature verification with invalid public key"""
        mock_load_key.side_effect = ValueError("Invalid key format")
        
        verification_data = {
            "message": "test_message",
            "signature_url_safe": "dGVzdF9zaWduYXR1cmU="  # base64 for "test_signature"
        }
        
        result = self.client.verify_sofizpay_signature(verification_data)
        assert result is False
    
    def test_verify_sofizpay_signature_url_safe_conversion(self):
        """Test URL-safe base64 conversion in signature verification"""
        # Test with URL-safe characters
        verification_data = {
            "message": "test_message",
            "signature_url_safe": "dGVzdF9zaWduYXR1cmVfd2l0aF9zcGVjaWFsX2NoYXJz-_"
        }
        
        # This should not raise an exception during base64 conversion
        result = self.client.verify_sofizpay_signature(verification_data)
        # We expect False because it's not a real signature, but no exception
        assert result is False
    
    def test_verify_sofizpay_signature_empty_data(self):
        """Test signature verification with empty data"""
        verification_data = {
            "message": "",
            "signature_url_safe": ""
        }
        
        result = self.client.verify_sofizpay_signature(verification_data)
        assert result is False


class TestClientIntegration:
    """Integration tests for the complete client"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.client = SofizPayClient()
    
    def test_client_version(self):
        """Test client version is accessible"""
        assert hasattr(self.client, 'VERSION')
        assert self.client.VERSION == "1.0.0"
    
    def test_sofizpay_public_key_available(self):
        """Test SofizPay public key is available"""
        assert hasattr(self.client, 'SOFIZPAY_PUBLIC_KEY_PEM')
        assert 'BEGIN PUBLIC KEY' in self.client.SOFIZPAY_PUBLIC_KEY_PEM
        assert 'END PUBLIC KEY' in self.client.SOFIZPAY_PUBLIC_KEY_PEM
    
    @pytest.mark.asyncio
    async def test_context_manager_support(self):
        """Test async context manager support"""
        async with SofizPayClient() as client:
            assert isinstance(client, SofizPayClient)
            # Test that we can access methods
            assert hasattr(client, 'make_cib_transaction')
            assert hasattr(client, 'verify_sofizpay_signature')


if __name__ == "__main__":
    pytest.main([__file__])
