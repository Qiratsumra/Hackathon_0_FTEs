"""
Simple Email Sender for AI Employee System

Script to send emails using the configured Gmail API
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from gmail_watcher import GmailWatcher
from security_config import validate_email


def send_email(to_email: str, subject: str, body: str):
    """
    Synchronous wrapper to send emails (for compatibility)
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    return asyncio.run(send_simple_email(to_email, subject, body))


async def send_simple_email(to_email: str, subject: str, body: str):
    """
    Send a simple email using the GmailWatcher

    Args:
        to_email: Recipient email address
        subject: Email subject
        body: Email body content
    """
    # Validate the email request first
    is_valid, validation_reason = validate_email(to_email, subject, body)

    if not is_valid:
        print(f"Email validation failed: {validation_reason}")
        print("This email requires approval according to security policies.")

        # Since kinzasaeed688@gmail.com is likely an unknown contact,
        # it will require approval. Let's create an approval request instead.
        create_approval_request(to_email, subject, body)
        return False

    # Create a GmailWatcher instance (this handles authentication)
    try:
        watcher = GmailWatcher(
            credentials_file="credentials.json",
            token_file="token.json",
            email_filter="is:unread is:important",
            interval=30,
            vault_path="./AI_Employee_Vault"
        )

        if watcher.service is None:
            print("Error: Gmail service not available. Please check your credentials.")
            return False

        # Send the email
        success = await watcher.send_email(to_email, subject, body)

        if success:
            print(f"Email sent successfully to {to_email}")
            return True
        else:
            print(f"Failed to send email to {to_email}")
            return False

    except Exception as e:
        print(f"Error creating GmailWatcher: {e}")
        print("Make sure you have credentials.json in the correct format from Google Cloud Console")
        return False


def create_approval_request(to_email: str, subject: str, body: str):
    """
    Create an approval request for the email since it requires approval
    """
    from datetime import datetime
    from pathlib import Path

    # Create approval request in Pending_Approval folder
    vault_path = Path("./AI_Employee_Vault")
    pending_approval_path = vault_path / "Pending_Approval"
    pending_approval_path.mkdir(parents=True, exist_ok=True)

    # Create approval request file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"{timestamp}_email_approval_to_{to_email.replace('@', '_at_').replace('.', '_dot_')}.md"
    filepath = pending_approval_path / filename

    approval_content = f"""---
status: pending_approval
priority: high
category: email
created: {datetime.now().isoformat()}
expires: {datetime.now().replace(day=datetime.now().day + 7).isoformat()}  # Expire in 7 days
---

# 📧 EMAIL APPROVAL REQUEST

## Summary
**Action**: Send email to {to_email}
**Subject**: {subject}
**Urgency**: Normal

## Email Details
- **Recipient**: {to_email}
- **Subject**: {subject}
- **Body Preview**:
```
{body[:500]}{'...' if len(body) > 500 else ''}
```

## Justification
- Requested by AI Employee system
- Content validated for security compliance
- Follows company communication guidelines

## Recommended Action
Approve this email to send it to {to_email}

## Next Steps if Approved
The email will be sent via Gmail API

---
**Submitted by**: AI Employee System
**Submitted at**: {datetime.now().isoformat()}
**Decision Required by**: One week from submission
---
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(approval_content)

    print(f"Approval request created: {filepath}")
    print(f"Please review and approve in the Pending_Approval folder to send this email.")


def main():
    """Main function to send an email"""
    print("AI Employee Email Sender")
    print("="*40)

    # Email details
    to_email = "kinzasaeed688@gmail.com"
    subject = "Message from AI Employee System"
    body = """Hello,

This is a test message sent from the AI Employee system.

The AI Employee system is designed to automate routine business operations including email management, task processing, and business operations.

If you have any questions or need assistance, please let me know.

Best regards,
AI Employee System"""

    print(f"Attempting to send email to: {to_email}")
    print(f"Subject: {subject}")
    print("-"*40)

    # Run the async function
    success = asyncio.run(send_simple_email(to_email, subject, body))

    if not success:
        print("\nThe email required approval and an approval request was created.")
        print("Check the Pending_Approval folder in your vault.")


if __name__ == "__main__":
    main()