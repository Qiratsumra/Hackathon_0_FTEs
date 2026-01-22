"""
Payment MCP Server

This module implements the payment MCP server for processing payments and financial transactions.
"""

import asyncio
import json
import sys
from typing import Dict, Any
from decimal import Decimal
import os
import uuid
from datetime import datetime


class PaymentMCP:
    """MCP server for payment operations."""

    def __init__(self):
        # In a real implementation, this would connect to a payment provider
        # For now, we'll simulate the operations
        self.transactions = []
        self.provider = os.getenv("PAYMENT_PROVIDER", "simulated")
        self.api_key = os.getenv("PAYMENT_API_KEY")

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        method = request.get('method')

        try:
            if method == 'process_payment':
                return await self.process_payment(request.get('params', {}))
            elif method == 'create_invoice':
                return await self.create_invoice(request.get('params', {}))
            elif method == 'check_balance':
                return await self.check_balance(request.get('params', {}))
            elif method == 'transfer_funds':
                return await self.transfer_funds(request.get('params', {}))
            else:
                return {
                    'error': {
                        'code': -32601,
                        'message': f'Method {method} not found'
                    }
                }
        except Exception as e:
            return {
                'error': {
                    'code': -32603,
                    'message': f'Internal error: {str(e)}'
                }
            }

    async def process_payment(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Process a payment transaction."""
        try:
            amount = params.get('amount')
            currency = params.get('currency', 'USD')
            to_account = params.get('to_account')
            from_account = params.get('from_account')
            description = params.get('description', '')
            payment_method = params.get('payment_method', 'card')

            if not amount or not to_account:
                return {'error': {'code': -32602, 'message': 'Amount and to_account are required'}}

            # Validate amount
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal <= 0:
                    return {'error': {'code': -32602, 'message': 'Amount must be positive'}}
            except:
                return {'error': {'code': -32602, 'message': 'Invalid amount format'}}

            # Generate transaction ID
            transaction_id = str(uuid.uuid4())

            # Simulate payment processing
            # In a real implementation, this would call the payment provider API
            transaction = {
                'id': transaction_id,
                'amount': float(amount_decimal),
                'currency': currency,
                'to_account': to_account,
                'from_account': from_account,
                'description': description,
                'payment_method': payment_method,
                'status': 'completed',
                'timestamp': datetime.now().isoformat(),
                'provider': self.provider
            }

            # Add to transaction history
            self.transactions.append(transaction)

            return {
                'result': {
                    'success': True,
                    'transaction_id': transaction_id,
                    'status': 'completed',
                    'details': transaction
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Payment processing failed: {str(e)}'}}

    async def create_invoice(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an invoice."""
        try:
            amount = params.get('amount')
            currency = params.get('currency', 'USD')
            to_account = params.get('to_account')
            description = params.get('description', '')
            due_date = params.get('due_date')
            items = params.get('items', [])

            if not amount or not to_account:
                return {'error': {'code': -32602, 'message': 'Amount and to_account are required'}}

            # Generate invoice ID
            invoice_id = f"INV-{uuid.uuid4().hex[:8].upper()}"

            # Create invoice object
            invoice = {
                'id': invoice_id,
                'amount': float(Decimal(str(amount))),
                'currency': currency,
                'to_account': to_account,
                'description': description,
                'due_date': due_date,
                'items': items,
                'status': 'created',
                'created_at': datetime.now().isoformat()
            }

            return {
                'result': {
                    'success': True,
                    'invoice_id': invoice_id,
                    'invoice': invoice
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Invoice creation failed: {str(e)}'}}

    async def check_balance(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Check account balance."""
        try:
            account_id = params.get('account_id')

            if not account_id:
                return {'error': {'code': -32602, 'message': 'Account ID is required'}}

            # In a real implementation, this would call the payment provider API
            # For simulation, return a random balance
            import random
            balance = round(random.uniform(1000, 10000), 2)

            return {
                'result': {
                    'success': True,
                    'account_id': account_id,
                    'balance': balance,
                    'currency': 'USD',
                    'as_of': datetime.now().isoformat()
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Balance check failed: {str(e)}'}}

    async def transfer_funds(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Transfer funds between accounts."""
        try:
            amount = params.get('amount')
            from_account = params.get('from_account')
            to_account = params.get('to_account')
            description = params.get('description', '')

            if not amount or not from_account or not to_account:
                return {'error': {'code': -32602, 'message': 'Amount, from_account, and to_account are required'}}

            # Validate amount
            try:
                amount_decimal = Decimal(str(amount))
                if amount_decimal <= 0:
                    return {'error': {'code': -32602, 'message': 'Amount must be positive'}}
            except:
                return {'error': {'code': -32602, 'message': 'Invalid amount format'}}

            # Generate transfer ID
            transfer_id = f"TRF-{uuid.uuid4().hex[:8].upper()}"

            # Create transfer record
            transfer = {
                'id': transfer_id,
                'amount': float(amount_decimal),
                'from_account': from_account,
                'to_account': to_account,
                'description': description,
                'status': 'completed',
                'timestamp': datetime.now().isoformat()
            }

            # Add to transaction history
            self.transactions.append(transfer)

            return {
                'result': {
                    'success': True,
                    'transfer_id': transfer_id,
                    'status': 'completed',
                    'details': transfer
                }
            }
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Fund transfer failed: {str(e)}'}}


async def run_server():
    """Run the payment MCP server."""
    server = PaymentMCP()

    # Read from stdin and write responses to stdout
    for line in sys.stdin:
        try:
            request = json.loads(line.strip())
            response = await server.handle_request(request)

            # Add the request ID to the response
            response['id'] = request.get('id')

            # Write response to stdout
            print(json.dumps(response), flush=True)
        except json.JSONDecodeError:
            error_response = {
                'id': None,
                'error': {
                    'code': -32700,
                    'message': 'Parse error'
                }
            }
            print(json.dumps(error_response), flush=True)
        except Exception as e:
            error_response = {
                'id': None,
                'error': {
                    'code': -32603,
                    'message': f'Server error: {str(e)}'
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == '__main__':
    asyncio.run(run_server())