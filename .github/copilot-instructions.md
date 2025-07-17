<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

# SofizPay SDK Python Project Instructions

This is a Python SDK for SofizPay that integrates with the Stellar network for cryptocurrency payments and transactions.

## Key Components:
- **Stellar Integration**: Uses stellar-sdk for blockchain operations
- **DZT Asset**: Custom asset with issuer GCAZI7YBLIDJWIVEL7ETNAZGPP3LC24NO6KAOBWZHUERXQ7M5BC52DLV
- **Payment Processing**: Send and receive DZT payments
- **Transaction Monitoring**: Real-time transaction streaming
- **Balance Management**: Check DZT balances
- **Transaction History**: Retrieve transaction records

## Coding Guidelines:
- Follow Python PEP 8 style guidelines
- Use type hints for better code clarity
- Include comprehensive error handling
- Add detailed docstrings for all functions
- Use async/await for network operations
- Implement retry logic for API calls
- Handle Stellar network rate limits properly

## Architecture:
- `sofizpay/client.py`: Main SDK client class
- `sofizpay/payments.py`: Payment operations
- `sofizpay/transactions.py`: Transaction management
- `sofizpay/utils.py`: Utility functions
- `sofizpay/exceptions.py`: Custom exceptions
