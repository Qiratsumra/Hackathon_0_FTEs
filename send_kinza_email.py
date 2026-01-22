"""
Email Sender for AI Employee System

Script to send emails using the configured Gmail API
"""

import asyncio
import os
import sys
from pathlib import Path

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from gmail_watcher import GmailWatcher
from security_config import security_config, validate_email


async def send_email_to_kinza():
    """
    Send an email to kinzasaeed688@gmail.com
    """
    # Email details
    to_email = "kinzasaeed688@gmail.com"
    subject = "Hello from AI Employee System"
    body = """Hello Kinza,

This is a message sent from the AI Employee system that I'm building to automate business operations.

The AI Employee system is designed to handle routine tasks like email management, file processing, and business operations automatically.

Hope you're doing well!

Best regards,
Bilal's AI Employee System"""

    print(f"Attempting to send email to: {to_email}")
    print(f"Subject: {subject}")
    print("-" * 40)

    # Check if the contact is known
    is_known = security_config.is_known_contact(to_email)
    print(f"Is contact known: {is_known}")

    # Validate the email request
    is_valid, validation_reason = validate_email(to_email, subject, body)
    print(f"Email validation: {is_valid}")
    print(f"Validation reason: {validation_reason}")

    if not is_valid and "unknown contact" in validation_reason.lower():
        print("\nThis email requires approval because it's to an unknown contact.")
        print("Creating an approval request...")

        # Create approval request in Pending_Approval folder
        create_approval_request(to_email, subject, body)
        return

    try:
        # Create a GmailWatcher instance (this handles authentication)
        watcher = GmailWatcher(
            credentials_file="credentials.json",  # Make sure this file exists
            token_file="token.json",             # Token will be created after first auth
            email_filter="is:unread is:important",
            interval=30,
            vault_path="./AI_Employee_Vault"
        )

        if watcher.service is None:
            print("Error: Gmail service not available. Please check your credentials.")
            print("Make sure you have credentials.json in the correct format from Google Cloud Console")
            return

        # Send the email
        print("Sending email...")
        success = await watcher.send_email(to_email, subject, body)

        if success:
            print(f"✅ Email sent successfully to {to_email}")
        else:
            print(f"❌ Failed to send email to {to_email}")

    except Exception as e:
        print(f"❌ Error sending email: {e}")
        print("Make sure:")
        print("1. credentials.json exists in the current directory")
        print("2. It has the correct format from Google Cloud Console")
        print("3. You have enabled Gmail API in your Google Cloud project")


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
priority: medium
category: email
created: {datetime.now().isoformat()}
---

# 📧 EMAIL APPROVAL REQUEST

## Summary
**Action**: Send email to {to_email}
**Subject**: {subject}
**Urgency**: Normal

## Email Details
- **Recipient**: {to_email}
- **Subject**: {subject}
- **Body**:
```
{body}
```

## Justification
- Part of AI Employee system testing
- Following proper email templates and guidelines
- Valid business communication

## Recommended Action
Review and approve this email to send it to {to_email}

## Next Steps if Approved
The email will be sent via Gmail API

---
**Submitted by**: AI Employee System
**Submitted at**: {datetime.now().isoformat()}
**Contact**: For questions about this request, check Company_Handbook.md
---
"""

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(approval_content)

    print(f"✅ Approval request created: {filepath}")
    print(f"Please review the file in the Pending_Approval folder to approve sending this email.")


def main():
    """Main function to send an email to kinza"""
    print("AI Employee Email Sender")
    print("="*50)

    # Run the async function
    asyncio.run(send_email_to_kinza())


if __name__ == "__main__":
    main()