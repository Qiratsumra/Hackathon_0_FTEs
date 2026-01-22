"""
Gmail Watcher for AI Employee System

Monitors Gmail account for new emails and creates task files
in the Needs_Action/ folder when important emails are detected.

Author: AI Employee System
Created: 2026-01-22
"""

import os
import time
import asyncio
import base64
import json
from pathlib import Path
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from base_watcher import BaseWatcher


try:
    import google.auth
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError

    GOOGLE_AVAILABLE = True
except ImportError:
    GOOGLE_AVAILABLE = False
    print("Google API libraries not available. Install with: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.modify']


class GmailWatcher(BaseWatcher):
    """
    Gmail watcher that monitors a Gmail account for new emails.

    Creates markdown task files in Needs_Action/ when important emails are detected.
    """

    def __init__(self,
                 credentials_file: str = "credentials.json",
                 token_file: str = "token.json",
                 email_filter: str = "is:unread from:me is:important",
                 interval: int = 30,
                 vault_path: str = "~/AI_Employee_Vault"):
        """
        Initialize the Gmail watcher.

        Args:
            credentials_file (str): Path to Google API credentials file
            token_file (str): Path to stored authentication token
            email_filter (str): Gmail search filter for important emails
            interval (int): Polling interval in seconds
            vault_path (str): Path to the Obsidian vault
        """
        super().__init__("GmailWatcher", interval, vault_path)

        if not GOOGLE_AVAILABLE:
            raise ImportError("Google API libraries are required for GmailWatcher. "
                            "Install with: pip install google-api-python-client google-auth google-auth-oauthlib google-auth-httplib2")

        self.credentials_file = Path(credentials_file).expanduser()
        self.token_file = Path(token_file).expanduser()
        self.email_filter = email_filter

        # Track seen email IDs to avoid duplicates
        self.seen_emails = set()
        self.load_seen_emails()

        # Gmail service
        self.service = None
        self.authenticate()

        self.logger.info(f"Initialized GmailWatcher")
        self.logger.info(f"Monitoring with filter: {self.email_filter}")
        self.logger.info(f"Polling interval: {self.interval}s")

    def authenticate(self):
        """Authenticate with Gmail API."""
        creds = None

        # Load existing token
        if self.token_file.exists():
            try:
                creds = Credentials.from_authorized_user_file(str(self.token_file), SCOPES)
            except Exception as e:
                self.logger.error(f"Error loading token: {e}")
                self.token_file.unlink(missing_ok=True)  # Remove invalid token file

        # If there are no valid credentials, request authorization
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.error(f"Error refreshing token: {e}")
                    if self.token_file.exists():
                        self.token_file.unlink(missing_ok=True)
                    creds = None

            if not creds:
                if not self.credentials_file.exists():
                    self.logger.error(f"Credentials file {self.credentials_file} not found")
                    self.logger.error("Please download credentials.json from Google Cloud Console")
                    return

                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        str(self.credentials_file), SCOPES)
                    creds = flow.run_local_server(port=0)
                except Exception as e:
                    self.logger.error(f"Error during OAuth flow: {e}")
                    return

            # Save credentials for next run
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())

        try:
            self.service = build('gmail', 'v1', credentials=creds)
            self.logger.info("Successfully authenticated with Gmail API")
        except Exception as e:
            self.logger.error(f"Error building Gmail service: {e}")
            self.service = None

    def load_seen_emails(self):
        """Load previously seen email IDs from a tracking file."""
        tracking_file = self.logs_path / "seen_emails.txt"
        if tracking_file.exists():
            try:
                with open(tracking_file, 'r') as f:
                    self.seen_emails = set(line.strip() for line in f if line.strip())
            except Exception as e:
                self.logger.error(f"Failed to load seen emails: {e}")

    def save_seen_emails(self):
        """Save seen email IDs to tracking file."""
        tracking_file = self.logs_path / "seen_emails.txt"
        try:
            with open(tracking_file, 'w') as f:
                for email_id in self.seen_emails:
                    f.write(f"{email_id}\n")
        except Exception as e:
            self.logger.error(f"Failed to save seen emails: {e}")

    def decode_email_body(self, message):
        """Decode the email body from base64."""
        payload = message.get('payload')
        headers = payload.get('headers', [])

        # Get subject and sender
        subject = ''
        sender = ''
        for header in headers:
            if header.get('name') == 'Subject':
                subject = header.get('value', '')
            elif header.get('name') == 'From':
                sender = header.get('value', '')

        # Get body
        body = ''
        if 'parts' in payload:
            # Multi-part email
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    body_data = part['body']['data']
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
                    break
                elif part['mimeType'] == 'text/html' and not body:
                    # Fallback to HTML if no plain text
                    body_data = part['body']['data']
                    body = base64.urlsafe_b64decode(body_data).decode('utf-8')
        else:
            # Single-part email
            body_data = payload['body']['data']
            body = base64.urlsafe_b64decode(body_data).decode('utf-8')

        return {
            'subject': subject,
            'sender': sender,
            'body': body,
            'headers': headers
        }

    async def check_for_new_items(self) -> List[Dict[str, Any]]:
        """
        Check for new emails in the Gmail account.

        Returns:
            list: List of new email dictionaries to process
        """
        if not self.service:
            self.logger.error("Gmail service not available")
            return []

        try:
            # Query for emails
            results = self.service.users().messages().list(
                userId='me',
                q=self.email_filter,
                maxResults=20  # Limit to avoid overwhelming
            ).execute()

            messages = results.get('messages', [])
            new_emails = []

            for msg in messages:
                email_id = msg['id']

                # Skip if we've already seen this email
                if email_id in self.seen_emails:
                    continue

                try:
                    # Get full email details
                    email_details = self.service.users().messages().get(
                        userId='me',
                        id=email_id
                    ).execute()

                    # Decode email content
                    decoded_email = self.decode_email_body(email_details)
                    decoded_email['id'] = email_id
                    decoded_email['internal_date'] = email_details.get('internalDate', '')

                    # Check for attachments
                    has_attachments = 'parts' in email_details.get('payload', {}) and \
                                   any(part.get('filename') for part in email_details['payload'].get('parts', []))
                    decoded_email['has_attachments'] = has_attachments

                    # Get labels
                    labels = email_details.get('labelIds', [])
                    decoded_email['labels'] = labels

                    new_emails.append(decoded_email)
                    self.seen_emails.add(email_id)

                except Exception as e:
                    self.logger.error(f"Error processing email {email_id}: {e}")
                    continue

            # Save seen emails periodically
            if len(self.seen_emails) % 10 == 0:  # Every 10 new emails
                self.save_seen_emails()

            self.logger.info(f"Found {len(new_emails)} new emails matching filter '{self.email_filter}'")
            return new_emails

        except Exception as e:
            self.logger.error(f"Error checking for new emails: {e}")
            # Re-authenticate if there's an authentication error
            if "invalid_grant" in str(e) or "unauthorized" in str(e).lower():
                self.logger.info("Authentication error detected, attempting re-authentication")
                if self.token_file.exists():
                    self.token_file.unlink()  # Remove invalid token
                self.authenticate()  # Re-authenticate
            return []

    def format_item_as_task(self, email: Dict[str, Any]) -> Tuple[str, str, Dict[str, Any]]:
        """
        Format an email as a task title and content.

        Args:
            email (dict): Email dictionary from Gmail API

        Returns:
            tuple: (title, content, metadata) for the task file
        """
        sender = email.get('sender', 'Unknown Sender')
        subject = email.get('subject', '(No Subject)')
        body = email.get('body', '(No Body)')

        # Extract sender name and email
        sender_name = sender
        sender_email = ""
        if '<' in sender and '>' in sender:
            parts = sender.split('<')
            if len(parts) > 1:
                sender_name = parts[0].strip().strip('"')
                sender_email = parts[1].strip('>')

        # Determine priority based on labels and content
        labels = email.get('labels', [])
        priority = 'medium'
        if 'IMPORTANT' in labels or 'CATEGORY_PERSONAL' in labels:
            priority = 'high'
        elif 'CATEGORY_UPDATES' in labels:
            priority = 'low'

        # Check if sender is in known contacts (would require additional logic to check contacts)
        # For now, we'll assume known contacts based on common business domains or previously seen senders
        is_known_contact = any(domain in sender_email for domain in [
            'gmail.com', 'outlook.com', 'yahoo.com', 'company.com', 'client.com'
        ]) or sender_name in ['Your Boss', 'Important Client']  # Placeholder logic

        # Determine if approval needed
        requires_approval = not is_known_contact or any(word in subject.lower() for word in [
            'payment', 'contract', 'agreement', 'money', 'invoice', 'budget'
        ])

        # Create title
        title = f"Email: {subject} from {sender_name}"

        # Create content
        content = f"""## Email Details
- **From:** {sender}
- **Subject:** {subject}
- **Date:** {email.get('internal_date', 'Unknown')}
- **Labels:** {', '.join(labels) if labels else 'None'}
- **Attachments:** {'Yes' if email.get('has_attachments') else 'No'}

## Email Body
{body}

## Processing Instructions
Based on the sender and content:

1. **Priority:** {priority.upper()}
2. **Known Contact:** {'Yes' if is_known_contact else 'No'}
3. **Approval Required:** {'Yes' if requires_approval else 'No'}

{'## ⚠️ APPROVAL REQUIRED' if requires_approval else ''}

{'This email is from an unknown contact and requires human approval before responding.' if not is_known_contact else ''}

{'This email contains financial/business terms and requires approval before responding.' if requires_approval and 'payment' in body.lower() else ''}

### Response Guidelines
- Keep response professional and concise
- Follow the email response templates in the Company_Handbook.md
- If approval is required, create an approval request in Pending_Approval folder
- If from known contact, respond using appropriate template
"""

        # Create metadata
        metadata = {
            'priority': priority,
            'category': 'email',
            'email_sender': sender_email,
            'email_subject': subject,
            'email_date': email.get('internal_date'),
            'is_known_contact': is_known_contact,
            'requires_approval': requires_approval,
            'action_required': 'respond' if not requires_approval else 'approval_needed',
            'gmail_id': email.get('id'),
            'labels': labels
        }

        return title, content, metadata

    async def send_email(self, to: str, subject: str, body: str, sender_email: str = "me") -> bool:
        """
        Send an email using the Gmail API.

        Args:
            to (str): Recipient email address
            subject (str): Email subject
            body (str): Email body
            sender_email (str): Sender (usually "me" for authenticated user)

        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.service:
            self.logger.error("Gmail service not available")
            return False

        try:
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject

            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

            # Send message
            sent_message = self.service.users().messages().send(
                userId=sender_email,
                body={'raw': raw_message}
            ).execute()

            self.logger.info(f"Email sent successfully to {to}, message ID: {sent_message['id']}")
            return True

        except Exception as e:
            self.logger.error(f"Error sending email to {to}: {e}")
            return False

    def cleanup_old_seen_emails(self):
        """
        Clean up old email IDs that are no longer in the mailbox.
        """
        try:
            # Get all messages matching our filter
            results = self.service.users().messages().list(
                userId='me',
                q=self.email_filter,
                maxResults=1000  # Reasonable upper limit
            ).execute()

            current_emails = {msg['id'] for msg in results.get('messages', [])}

            # Remove IDs for emails that no longer match the filter
            old_ids = self.seen_emails - current_emails
            self.seen_emails = current_emails

            if old_ids:
                self.logger.info(f"Removed {len(old_ids)} old email IDs from tracking")
                self.save_seen_emails()

        except Exception as e:
            self.logger.error(f"Error cleaning up old seen emails: {e}")


async def main():
    """
    Main function to run the Gmail watcher.
    """
    # Create Gmail watcher instance
    watcher = GmailWatcher(
        credentials_file="credentials.json",  # You'll need to obtain this from Google Cloud Console
        token_file="token.json",  # Will be created automatically after first auth
        email_filter="is:unread is:important",  # Adjust filter as needed
        interval=30,  # Check every 30 seconds
        vault_path="~/AI_Employee_Vault"
    )

    try:
        print(f"Starting GmailWatcher...")
        print(f"Monitoring with filter: {watcher.email_filter}")
        print(f"Output to: {watcher.needs_action_path}")
        print("Note: You may need to authenticate with Google on first run")
        print("Press Ctrl+C to stop")

        await watcher.run()

    except KeyboardInterrupt:
        print("\nStopping GmailWatcher...")
        watcher.stop()

        # Save seen emails before exiting
        watcher.save_seen_emails()

    except Exception as e:
        print(f"Error running GmailWatcher: {e}")
        watcher.logger.error(f"Fatal error: {e}")


if __name__ == "__main__":
    asyncio.run(main())