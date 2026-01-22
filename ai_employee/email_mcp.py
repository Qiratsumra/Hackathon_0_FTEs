"""
Email MCP Server

This module implements the email MCP server for sending/receiving emails via Gmail API.
"""

import asyncio
import json
import smtplib
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any
from pathlib import Path
import os
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class EmailMCP:
    """MCP server for email operations."""

    def __init__(self):
        # Gmail API scopes
        self.scopes = ['https://www.googleapis.com/auth/gmail.send',
                      'https://www.googleapis.com/auth/gmail.readonly']

        # Load credentials
        self.creds = None
        self.service = None

        # Try to load existing credentials
        token_path = Path("token.json")
        creds_path = Path("credentials.json")

        if token_path.exists():
            self.creds = Credentials.from_authorized_user_file(str(token_path), self.scopes)

        # If there are no (valid) credentials available, let the user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                try:
                    self.creds.refresh(Request())
                except Exception:
                    # If refresh fails, we need to re-authenticate
                    if creds_path.exists():
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(creds_path), self.scopes)
                        self.creds = flow.run_local_server(port=0)
            elif creds_path.exists():
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(creds_path), self.scopes)
                self.creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            if self.creds:
                with open(token_path, 'w') as token:
                    token.write(self.creds.to_json())

        if self.creds:
            try:
                self.service = build('gmail', 'v1', credentials=self.creds)
            except Exception as e:
                print(f"Error initializing Gmail service: {e}", file=sys.stderr)

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle an MCP request."""
        method = request.get('method')

        try:
            if method == 'send_email':
                return await self.send_email(request.get('params', {}))
            elif method == 'get_email':
                return await self.get_email(request.get('params', {}))
            elif method == 'list_emails':
                return await self.list_emails(request.get('params', {}))
            elif method == 'create_draft':
                return await self.create_draft(request.get('params', {}))
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

    def _gmail_message_to_dict(self, msg):
        """Convert Gmail message to dictionary format."""
        payload = msg.get('payload', {})
        headers = payload.get('headers', [])

        header_map = {}
        for header in headers:
            header_map[header['name']] = header['value']

        return {
            'id': msg.get('id'),
            'threadId': msg.get('threadId'),
            'snippet': msg.get('snippet'),
            'internalDate': msg.get('internalDate'),
            'subject': header_map.get('Subject', ''),
            'from': header_map.get('From', ''),
            'to': header_map.get('To', ''),
            'cc': header_map.get('Cc', ''),
            'bcc': header_map.get('Bcc', ''),
            'date': header_map.get('Date', ''),
            'body': self._extract_body(payload)
        }

    def _extract_body(self, payload):
        """Extract email body from payload."""
        body = ''
        parts = payload.get('parts', [])

        if not parts:
            # If there are no parts, the body might be in the payload directly
            body_data = payload.get('body', {}).get('data')
            if body_data:
                body = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')
        else:
            # Look for the text/plain part
            for part in parts:
                if part.get('mimeType') == 'text/plain':
                    body_data = part.get('body', {}).get('data')
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')
                        break
                elif part.get('mimeType') == 'multipart/alternative':
                    # Recursively check sub-parts
                    sub_parts = part.get('parts', [])
                    for sub_part in sub_parts:
                        if sub_part.get('mimeType') == 'text/plain':
                            body_data = sub_part.get('body', {}).get('data')
                            if body_data:
                                body = base64.urlsafe_b64decode(body_data.encode('ASCII')).decode('utf-8')
                                break
                    if body:
                        break

        return body

    async def send_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send an email via Gmail API."""
        if not self.service:
            return {'error': {'code': -32603, 'message': 'Gmail service not initialized'}}

        try:
            to = params.get('to')
            subject = params.get('subject')
            body = params.get('body', '')
            cc = params.get('cc', [])
            bcc = params.get('bcc', [])

            if not to or not subject:
                return {'error': {'code': -32602, 'message': 'To and subject are required'}}

            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = ', '.join(cc) if isinstance(cc, list) else cc
            if bcc:
                message['bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc

            # Add body to email
            message.attach(MIMEText(body, 'plain'))

            # Encode message
            raw_message = message.as_string()
            import base64
            encoded_message = base64.urlsafe_b64encode(raw_message.encode()).decode()

            # Create send object
            send_message = {'raw': encoded_message}

            # Send the message
            sent_message = self.service.users().messages().send(
                userId="me", body=send_message).execute()

            return {
                'result': {
                    'success': True,
                    'message_id': sent_message.get('id'),
                    'thread_id': sent_message.get('threadId')
                }
            }
        except HttpError as error:
            return {'error': {'code': -32603, 'message': f'Gmail API error: {error.error_details}'}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to send email: {str(e)}'}}

    async def get_email(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get an email by ID."""
        if not self.service:
            return {'error': {'code': -32603, 'message': 'Gmail service not initialized'}}

        email_id = params.get('id')
        if not email_id:
            return {'error': {'code': -32602, 'message': 'Email ID is required'}}

        try:
            # Get the message
            message = self.service.users().messages().get(
                userId="me", id=email_id).execute()

            email_dict = self._gmail_message_to_dict(message)

            return {'result': {'email': email_dict}}
        except HttpError as error:
            return {'error': {'code': -32603, 'message': f'Gmail API error: {error.error_details}'}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to get email: {str(e)}'}}

    async def list_emails(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """List emails with optional filters."""
        if not self.service:
            return {'error': {'code': -32603, 'message': 'Gmail service not initialized'}}

        try:
            # Parameters for listing
            q = params.get('query', '')  # Search query
            max_results = params.get('max_results', 10)  # Max number of results

            # List messages
            results = self.service.users().messages().list(
                userId="me", q=q, maxResults=max_results).execute()
            messages = results.get('messages', [])

            # Get detailed information for each message
            emails = []
            for msg in messages:
                try:
                    message = self.service.users().messages().get(
                        userId="me", id=msg['id']).execute()
                    email_dict = self._gmail_message_to_dict(message)
                    emails.append(email_dict)
                except Exception as e:
                    print(f"Error getting message {msg['id']}: {e}", file=sys.stderr)
                    continue

            return {'result': {'emails': emails, 'total': len(emails)}}
        except HttpError as error:
            return {'error': {'code': -32603, 'message': f'Gmail API error: {error.error_details}'}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to list emails: {str(e)}'}}

    async def create_draft(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Create an email draft."""
        if not self.service:
            return {'error': {'code': -32603, 'message': 'Gmail service not initialized'}}

        try:
            to = params.get('to')
            subject = params.get('subject')
            body = params.get('body', '')
            cc = params.get('cc', [])
            bcc = params.get('bcc', [])

            if not to or not subject:
                return {'error': {'code': -32602, 'message': 'To and subject are required'}}

            # Create message
            message = MIMEMultipart()
            message['to'] = to
            message['subject'] = subject

            if cc:
                message['cc'] = ', '.join(cc) if isinstance(cc, list) else cc
            if bcc:
                message['bcc'] = ', '.join(bcc) if isinstance(bcc, list) else bcc

            # Add body to email
            message.attach(MIMEText(body, 'plain'))

            # Encode message
            raw_message = message.as_string()
            import base64
            encoded_message = base64.urlsafe_b64encode(raw_message.encode()).decode()

            # Create draft object
            draft = {'message': {'raw': encoded_message}}

            # Create the draft
            draft_result = self.service.users().drafts().create(
                userId="me", body=draft).execute()

            return {
                'result': {
                    'success': True,
                    'draft_id': draft_result.get('id'),
                    'message_id': draft_result.get('message', {}).get('id')
                }
            }
        except HttpError as error:
            return {'error': {'code': -32603, 'message': f'Gmail API error: {error.error_details}'}}
        except Exception as e:
            return {'error': {'code': -32603, 'message': f'Failed to create draft: {str(e)}'}}


async def run_server():
    """Run the email MCP server."""
    server = EmailMCP()

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