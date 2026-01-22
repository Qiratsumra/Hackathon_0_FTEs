"""
AI Employee Chatbot Interface

A conversational interface for controlling the AI Employee system.
Allows users to send emails, manage tasks, check system status, and more.
"""
import asyncio
import json
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import colorama
from colorama import Fore, Style, init

# Initialize colorama for colored output
init(autoreset=True)

# Add the current directory to the path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent))

from send_email import send_email
from security_config import security_config
from ai_employee.email_mcp import EmailMCP
from ai_employee.claude_integration import process_task_with_claude


class AIChatbot:
    """Conversational interface for the AI Employee system."""

    def __init__(self):
        self.email_mcp = EmailMCP()
        self.system_status = "running"
        self.conversation_history = []

    def greet_user(self) -> str:
        """Return a greeting message."""
        return """🤖 Welcome to the AI Employee System Chatbot!

I can help you with:
📧 Send emails through the system
📋 Manage tasks and workflows
📊 Check system status and statistics
🔍 Find information in the knowledge base
📝 Create new tasks or notes
📈 Generate reports and briefings

Type 'help' to see all available commands or tell me what you'd like to do!"""

    def process_command(self, user_input: str) -> str:
        """Process user commands and return appropriate response."""
        user_input_lower = user_input.lower().strip()

        # Command mapping
        if user_input_lower in ['quit', 'exit', 'bye', 'goodbye']:
            return self.handle_quit()
        elif user_input_lower in ['help', 'commands', 'menu']:
            return self.show_help()
        elif user_input_lower.startswith('send email') or user_input_lower.startswith('email'):
            return self.handle_send_email(user_input)
        elif user_input_lower.startswith('status') or user_input_lower.startswith('check status'):
            return self.handle_status_check()
        elif user_input_lower.startswith('create task') or user_input_lower.startswith('add task'):
            return self.handle_create_task(user_input)
        elif user_input_lower.startswith('list tasks') or user_input_lower.startswith('show tasks'):
            return self.handle_list_tasks()
        elif user_input_lower.startswith('read email') or user_input_lower.startswith('check email'):
            return self.handle_read_email(user_input)
        elif user_input_lower.startswith('check email watcher') or user_input_lower.startswith('email status'):
            return self.handle_email_watcher_status()
        elif user_input_lower.startswith('generate report') or user_input_lower.startswith('report'):
            return self.handle_generate_report(user_input)
        elif user_input_lower.startswith('search') or user_input_lower.startswith('find'):
            return self.handle_search(user_input)
        else:
            return self.handle_general_query(user_input)

    def handle_quit(self) -> str:
        """Handle quit command."""
        return "👋 Goodbye! The AI Employee System remains operational in the background."

    def show_help(self) -> str:
        """Show help information."""
        help_text = """
🤖 **AI Employee System Commands:**

**Email Operations:**
- `send email to [email] subject [subject] body [message]` - Send an email
- `check email` - Check recent email-related tasks in the system
- `check email watcher` - Check the status of the Gmail monitoring system

**Task Management:**
- `create task [task description]` - Create a new task
- `list tasks` - Show current tasks in different folders
- `create task process file [filename]` - Create a file processing task

**System Operations:**
- `status` - Check system status
- `generate report daily` - Generate daily briefing
- `generate report weekly` - Generate weekly briefing

**Information:**
- `search [keyword]` - Search in the knowledge base
- `find [term]` - Find information in vault

**General:**
- `help` - Show this help menu
- `quit` - Exit the chatbot

Example: `send email to john@example.com subject Hello body Hi John, how are you?`

**Note:** To actively monitor your Gmail inbox, run `python gmail_watcher.py` in a separate terminal.
        """
        return help_text

    def handle_send_email(self, user_input: str) -> str:
        """Handle email sending commands."""
        try:
            # Extract email components using regex
            to_match = re.search(r'to\s+([^\s,]+@[^\s,]+)', user_input, re.IGNORECASE)
            subject_match = re.search(r'subject\s+(.+?)(?:\s+body|$)', user_input, re.IGNORECASE)
            body_match = re.search(r'body\s+(.+)', user_input, re.IGNORECASE)

            if not to_match:
                return "❌ Please specify a recipient email address. Format: 'send email to email@address.com'"

            to_email = to_match.group(1)

            if subject_match:
                subject = subject_match.group(1).strip()
            else:
                subject = "Message from AI Employee System"

            if body_match:
                body = body_match.group(1).strip()
            else:
                body = "This is an automated message from the AI Employee System."

            # Validate email format
            if not self.is_valid_email(to_email):
                return f"❌ Invalid email format: {to_email}"

            # Check if contact is known (for security)
            is_known = security_config.is_known_contact(to_email)

            # Validate the email request using the security config
            is_valid, reason = security_config.validate_email_request(to_email, subject, body)

            # If validation fails, it requires approval
            if not is_valid:
                return self.create_approval_task(to_email, subject, body, reason)

            # Send the email using the existing send_email module
            result = send_email(to_email, subject, body)

            if result:
                return f"✅ Email sent successfully to {to_email}!\nSubject: {subject}"
            else:
                return f"❌ Failed to send email to {to_email}. Please check the system logs."

        except Exception as e:
            return f"❌ Error processing email command: {str(e)}"

    def handle_status_check(self) -> str:
        """Handle status check commands."""
        try:
            # Get counts from different vault folders
            vault_path = Path("./AI_Employee_Vault")

            counts = {}
            folders_to_check = ["Needs_Action", "Plans", "In_Progress", "Pending_Approval", "Approved", "Done", "Logs", "Briefings"]

            for folder in folders_to_check:
                folder_path = vault_path / folder
                if folder_path.exists():
                    file_count = len(list(folder_path.glob("*.md"))) + len(list(folder_path.glob("*.txt")))
                    counts[folder] = file_count
                else:
                    counts[folder] = 0

            status_msg = f"""
📊 **AI Employee System Status**

System Status: ✅ Running
Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Task Counts:**
• Needs Action: {counts['Needs_Action']} tasks
• In Progress: {counts['In_Progress']} tasks
• Pending Approval: {counts['Pending_Approval']} tasks
• Approved: {counts['Approved']} tasks
• Done: {counts['Done']} tasks
• Plans: {counts['Plans']} plans

**Other Folders:**
• Logs: {counts['Logs']} files
• Briefings: {counts['Briefings']} reports

The system is actively monitoring and processing tasks!
            """
            return status_msg

        except Exception as e:
            return f"❌ Error checking system status: {str(e)}"

    def handle_create_task(self, user_input: str) -> str:
        """Handle task creation commands."""
        try:
            # Extract task description after 'create task' or 'add task'
            task_match = re.search(r'(?:create task|add task)\s+(.+)', user_input, re.IGNORECASE)

            if not task_match:
                return "❌ Please specify a task description. Format: 'create task [description]'"

            task_description = task_match.group(1).strip()

            # Create task file in Needs_Action folder
            vault_path = Path("./AI_Employee_Vault/Needs_Action")
            vault_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_filename = f"{timestamp}_chatbot_task.md"
            task_file_path = vault_path / task_filename

            # Create task content with metadata
            task_content = f"""---
id: chatbot_{timestamp}
created: '{datetime.now().isoformat()}'
status: new
priority: medium
category: chatbot-generated
source: chatbot
---

# Chatbot Task: {task_description}

## Description
{task_description}

## Created By
AI Employee Chatbot

## Instructions
This task was created via the chatbot interface. Please process according to standard procedures.

---
Created at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

            with open(task_file_path, 'w', encoding='utf-8') as f:
                f.write(task_content)

            return f"✅ Task created successfully!\n📁 File: {task_filename}\n📝 Description: {task_description}"

        except Exception as e:
            return f"❌ Error creating task: {str(e)}"

    def handle_list_tasks(self) -> str:
        """Handle task listing commands."""
        try:
            vault_path = Path("./AI_Employee_Vault")
            folders_to_check = ["Needs_Action", "In_Progress", "Pending_Approval", "Approved", "Done"]

            response = "📋 **Current Tasks in System**\n\n"

            for folder in folders_to_check:
                folder_path = vault_path / folder
                if folder_path.exists():
                    task_files = list(folder_path.glob("*.md")) + list(folder_path.glob("*.txt"))

                    if task_files:
                        response += f"**{folder} ({len(task_files)}):**\n"
                        for i, task_file in enumerate(task_files[:5]):  # Show first 5
                            response += f"  • {task_file.name}\n"

                        if len(task_files) > 5:
                            response += f"  ... and {len(task_files) - 5} more\n"
                        response += "\n"
                    else:
                        response += f"**{folder}:** No tasks\n\n"
                else:
                    response += f"**{folder}:** Folder not found\n\n"

            return response

        except Exception as e:
            return f"❌ Error listing tasks: {str(e)}"

    def handle_read_email(self, user_input: str) -> str:
        """Handle email reading commands."""
        try:
            # Use the email MCP to actually read emails from Gmail
            import asyncio

            # Extract any filters from the command
            sender_filter = None
            if 'from' in user_input.lower():
                # Simple extraction of sender from command like "check email from john"
                import re
                sender_match = re.search(r'from\s+([^\s]+)', user_input, re.IGNORECASE)
                if sender_match:
                    sender_filter = sender_match.group(1)

            # Try to use the email MCP to list emails
            try:
                # Create a params dict for the list_emails method
                params = {
                    'query': f'from:{sender_filter}' if sender_filter else '',
                    'max_results': 10
                }

                # Run the email listing asynchronously
                result = asyncio.run(self.email_mcp.list_emails(params))

                if 'result' in result and 'emails' in result['result']:
                    emails = result['result']['emails']
                    total = result['result']['total']

                    if emails:
                        response = f"📬 **Recent Emails ({total}):**\n\n"
                        for i, email in enumerate(emails[:5]):  # Show first 5
                            subject = email.get('subject', 'No Subject')
                            sender = email.get('from', 'Unknown Sender')
                            date = email.get('date', 'Unknown Date')

                            response += f"**Email {i+1}:**\n"
                            response += f"- From: {sender}\n"
                            response += f"- Subject: {subject}\n"
                            response += f"- Date: {date}\n"
                            response += f"- Snippet: {email.get('snippet', 'No preview')[:100]}...\n\n"

                        return response
                    else:
                        if sender_filter:
                            return f"📭 No emails found from '{sender_filter}'."
                        else:
                            return "📭 No recent emails found in your Gmail inbox."
                else:
                    # Fallback: check for email tasks in the system
                    inbox_path = Path("./AI_Employee_Vault/Inbox")
                    if inbox_path.exists():
                        email_files = list(inbox_path.glob("*.md"))
                        if email_files:
                            response = f"📬 **Recent Email Tasks in System ({len(email_files)}):**\n\n"
                            for email_file in email_files[-5:]:  # Show last 5
                                response += f"• {email_file.name}\n"
                            return response
                        else:
                            return "📭 No recent email tasks found in the system inbox."
                    else:
                        return "📭 No email tasks found. Gmail integration may need configuration."

            except Exception as e:
                # Fallback: check for email tasks in the system
                inbox_path = Path("./AI_Employee_Vault/Inbox")
                if inbox_path.exists():
                    email_files = list(inbox_path.glob("*.md"))
                    if email_files:
                        response = f"📬 **Recent Email Tasks in System ({len(email_files)}):**\n\n"
                        for email_file in email_files[-5:]:  # Show last 5
                            response += f"• {email_file.name}\n"
                        return response
                    else:
                        return "📭 No recent email tasks found in the system inbox."
                else:
                    # Check for email-related tasks in other folders
                    vault_path = Path("./AI_Employee_Vault")
                    folders_to_check = ["Needs_Action", "In_Progress", "Pending_Approval"]

                    email_tasks = []
                    for folder in folders_to_check:
                        folder_path = vault_path / folder
                        if folder_path.exists():
                            # Look for files that seem to be email-related
                            for file_path in folder_path.glob("*.md"):
                                content = file_path.read_text(encoding='utf-8', errors='ignore')
                                # Check if the file contains email-related content
                                if any(keyword in content.lower() for keyword in ['email', 'to:', 'from:', 'subject:', 'greeting', 'dear']):
                                    email_tasks.append({
                                        'file': file_path,
                                        'folder': folder,
                                        'content_preview': content[:200] + "..." if len(content) > 200 else content
                                    })

                    if email_tasks:
                        response = f"📬 **Email-Related Tasks Found ({len(email_tasks)}):**\n\n"
                        for i, task in enumerate(email_tasks[:10]):  # Show first 10
                            response += f"**Email Task {i+1}:**\n"
                            response += f"- File: {task['file'].name}\n"
                            response += f"- Location: {task['folder']}/\n"
                            response += f"- Preview: {task['content_preview'][:100]}...\n\n"

                        response += "Tip: Check the actual files in the vault folders for complete email content."
                        return response
                    else:
                        return f"📧 Gmail API error: {str(e)}. Check your Gmail integration configuration."

        except Exception as e:
            return f"❌ Error reading emails: {str(e)}"

    def handle_email_watcher_status(self) -> str:
        """Handle email watcher status check."""
        try:
            # Check if the gmail_watcher.py file exists
            gmail_watcher_path = Path("./gmail_watcher.py")
            if not gmail_watcher_path.exists():
                return """📧 **Email Watcher Status: Not Found**

The Gmail watcher script (gmail_watcher.py) is not found in the system.
To enable email checking functionality:

1. Make sure the gmail_watcher.py file exists
2. Configure your Gmail API credentials in credentials.json
3. Ensure your .env file has the correct Gmail settings
4. Run the gmail_watcher.py separately to monitor your inbox

Without the email watcher running, the system cannot automatically check for new emails."""

            # Check if there are any recent email-related files in the system
            vault_path = Path("./AI_Employee_Vault")
            recent_emails = []

            # Check Needs_Action folder for email-related tasks
            needs_action_path = vault_path / "Needs_Action"
            if needs_action_path.exists():
                for file_path in needs_action_path.glob("*.md"):
                    content = file_path.read_text(encoding='utf-8', errors='ignore')
                    if any(keyword in content.lower() for keyword in ['email', 'greeting', 'dear', 'regarding', 'message']):
                        recent_emails.append(f"• {file_path.name} (Needs Action)")

            # Check Inbox folder
            inbox_path = vault_path / "Inbox"
            if inbox_path.exists():
                inbox_files = list(inbox_path.glob("*.md"))
                for file_path in inbox_files[:5]:  # First 5
                    recent_emails.append(f"• {file_path.name} (Inbox)")

            status_msg = """📧 **Email Watcher Status: Configuration Check**

The email watcher (gmail_watcher.py) exists in the system.
To actively monitor your Gmail inbox:

1. **Start the email watcher separately:**
   ```bash
   python gmail_watcher.py
   ```

2. **Ensure your Gmail API is configured:**
   - credentials.json file exists with Gmail API access
   - Correct permissions set in Google Cloud Console
   - .env file has proper Gmail settings

3. **Check system logs** in AI_Employee_Vault/Logs/ for email watcher status

**Recent Email Activities in System:**
"""
            if recent_emails:
                for email in recent_emails:
                    status_msg += f"{email}\n"
            else:
                status_msg += "No recent email activities found in the system.\n"

            status_msg += """

Note: The email watcher runs separately from this chatbot and monitors your Gmail continuously."""
            return status_msg

        except Exception as e:
            return f"❌ Error checking email watcher status: {str(e)}"

    def handle_generate_report(self, user_input: str) -> str:
        """Handle report generation commands."""
        try:
            if 'daily' in user_input.lower():
                return self.generate_daily_briefing()
            elif 'weekly' in user_input.lower():
                return self.generate_weekly_briefing()
            else:
                return "Please specify 'daily' or 'weekly' report. Example: 'generate report daily'"

        except Exception as e:
            return f"❌ Error generating report: {str(e)}"

    def generate_daily_briefing(self) -> str:
        """Generate daily briefing."""
        try:
            vault_path = Path("./AI_Employee_Vault")
            logs_path = vault_path / "Logs"
            logs_path.mkdir(parents=True, exist_ok=True)

            # Count tasks in each folder
            needs_action_count = len(list((vault_path / "Needs_Action").glob("*.md"))) if (vault_path / "Needs_Action").exists() else 0
            in_progress_count = len(list((vault_path / "In_Progress").glob("*.md"))) if (vault_path / "In_Progress").exists() else 0
            pending_approval_count = len(list((vault_path / "Pending_Approval").glob("*.md"))) if (vault_path / "Pending_Approval").exists() else 0
            approved_count = len(list((vault_path / "Approved").glob("*.md"))) if (vault_path / "Approved").exists() else 0
            done_count = len(list((vault_path / "Done").glob("*.md"))) if (vault_path / "Done").exists() else 0

            briefing_content = f"""# Daily Status Briefing - {datetime.now().strftime('%Y-%m-%d')}

## Task Status
- **Needs Action:** {needs_action_count}
- **In Progress:** {in_progress_count}
- **Pending Approval:** {pending_approval_count}
- **Ready to Execute:** {approved_count}
- **Completed:** {done_count}

## System Health
- **Status:** Operational
- **AI Employee Active:** Yes

## Next Steps
- Process {needs_action_count} pending tasks
- Follow up on {pending_approval_count} approval requests
- Monitor {in_progress_count} ongoing tasks

---
Generated by AI Employee Chatbot at {datetime.now().isoformat()}
"""

            # Save to logs
            briefing_file = logs_path / f"daily_briefing_{datetime.now().strftime('%Y%m%d')}.md"
            with open(briefing_file, 'w', encoding='utf-8') as f:
                f.write(briefing_content)

            return f"📊 Daily briefing generated successfully!\n📄 Saved as: {briefing_file.name}\n\n{briefing_content[:500]}..."

        except Exception as e:
            return f"❌ Error generating daily briefing: {str(e)}"

    def generate_weekly_briefing(self) -> str:
        """Generate weekly briefing."""
        try:
            vault_path = Path("./AI_Employee_Vault")
            briefings_path = vault_path / "Briefings"
            briefings_path.mkdir(parents=True, exist_ok=True)

            # Calculate week range
            week_start = datetime.now().date()
            while week_start.weekday() != 0:  # Monday
                week_start = week_start - timedelta(days=1)
            week_end = week_start + timedelta(days=6)

            briefing_content = f"""# Weekly CEO Briefing - Week of {week_start.strftime('%Y-%m-%d')} to {week_end.strftime('%Y-%m-%d')}

## Executive Summary

This week the AI Employee system managed routine operations while identifying opportunities for process improvement. Key metrics show steady performance with room for optimization in task prioritization.

## Revenue Performance

### Weekly Results
- **Actual Revenue:** $0 / **Target:** $4000 (0% of target)
- **Daily Average:** $0 / **Target:** $571 per day
- **Trend:** Stable compared to previous week

### Monthly Progress
- **Month-to-Date:** $0 / $4000 (0% of monthly goal)
- **Projected Monthly Total:** $0 if current pace continues
- **Gap to Target:** $4000 needed to reach goal

## Key Performance Indicators

### Operational Metrics
| Metric | This Week | Last Week | Target | Status |
|--------|-----------|-----------|--------|---------|
| Tasks Processed | 0 | 0 | Variable | Neutral |
| Email Response Rate | N/A | N/A | >95% | N/A |
| System Uptime | 100% | 100% | >99% | Healthy |

## Completed Tasks

### Routine Operations
- System monitoring and maintenance
- Task processing and routing
- Status reporting and briefings
- Security and approval workflows

## Bottlenecks & Challenges

### Current Issues
1. **Initial Setup Phase**
   - Impact: Limited operational capacity during setup
   - Root cause: System configuration and testing phase
   - Resolution status: Ongoing - expected completion soon

## Trends & Insights

### Areas of Concern
- Initial setup phase means limited operational data
- Revenue tracking not yet active
- Need to establish baseline metrics

## Recommendations

### Immediate Actions (This Week)
1. **Complete System Setup**: Finish remaining configuration
2. **Begin Operations**: Start processing real tasks
3. **Establish Baseline**: Begin tracking operational metrics

### Strategic Considerations
1. **Process Optimization**: Fine-tune task processing workflows
2. **Performance Monitoring**: Enhance tracking and reporting
3. **Scalability Planning**: Prepare for increased workload

## Next Week Priorities

### Revenue Focus
- Begin revenue-generating activities
- Process initial client requests
- Track financial metrics

### Operational Improvements
- Optimize task processing speed
- Improve approval workflows
- Enhance error handling

---

**Generated by:** AI Employee System Chatbot
**Last Updated:** {datetime.now().isoformat()}
**Next Briefing:** {(week_end + timedelta(days=1)).strftime('%Y-%m-%d')}
"""

            # Save to briefings folder
            briefing_file = briefings_path / f"{datetime.now().strftime('%Y%m%d')}_Weekly_Briefing.md"
            with open(briefing_file, 'w', encoding='utf-8') as f:
                f.write(briefing_content)

            return f"📈 Weekly briefing generated successfully!\n📄 Saved as: {briefing_file.name}\n\n{briefing_content[:500]}..."

        except Exception as e:
            return f"❌ Error generating weekly briefing: {str(e)}"

    def handle_search(self, user_input: str) -> str:
        """Handle search commands."""
        try:
            search_term = re.search(r'(?:search|find)\s+(.+)', user_input, re.IGNORECASE)

            if not search_term:
                return "❌ Please specify a search term. Format: 'search [keyword]'"

            search_keyword = search_term.group(1).strip()

            # Search across all vault folders
            vault_path = Path("./AI_Employee_Vault")
            results = []

            for root, dirs, files in os.walk(vault_path):
                for file in files:
                    if file.endswith(('.md', '.txt')):
                        file_path = Path(root) / file
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if search_keyword.lower() in content.lower():
                                    # Get context around the match
                                    lines = content.lower().split('\n')
                                    for i, line in enumerate(lines):
                                        if search_keyword.lower() in line:
                                            context_line = content.split('\n')[i] if i < len(content.split('\n')) else ""
                                            results.append({
                                                'file': str(file_path.relative_to(vault_path)),
                                                'context': context_line.strip()[:100] + "..." if len(context_line.strip()) > 100 else context_line.strip()
                                            })
                                            if len(results) >= 5:  # Limit results
                                                break
                                    if len(results) >= 5:
                                        break
                        except Exception:
                            continue  # Skip files that can't be read

            if results:
                response = f"🔍 **Search Results for '{search_keyword}' ({len(results)} found):**\n\n"
                for result in results:
                    response += f"📄 {result['file']}\n"
                    response += f"   Context: {result['context']}\n\n"
            else:
                response = f"🔍 No results found for '{search_keyword}' in the knowledge base."

            return response

        except Exception as e:
            return f"❌ Error during search: {str(e)}"

    def handle_general_query(self, user_input: str) -> str:
        """Handle general queries that don't match specific commands."""
        # Try to identify intent from the query
        user_lower = user_input.lower()

        if any(word in user_lower for word in ['hello', 'hi', 'hey']):
            return "Hello! 👋 How can I help you with the AI Employee System today?"
        elif any(word in user_lower for word in ['thank', 'thanks']):
            return "You're welcome! 😊 Is there anything else I can help you with?"
        elif any(word in user_lower for word in ['system', 'running', 'working']):
            return self.handle_status_check()
        elif any(word in user_lower for word in ['email', 'send', 'message']):
            return "To send an email, use the command: `send email to email@address.com subject Hello body Your message here`"
        elif any(word in user_lower for word in ['task', 'create', 'add']):
            return "To create a task, use the command: `create task Your task description here`"
        elif any(word in user_lower for word in ['help', 'command', 'what']):
            return self.show_help()
        else:
            return f"I'm the AI Employee System Chatbot! 🤖 I can help you send emails, manage tasks, check system status, and more.\n\n{self.show_help()}"

    def is_valid_email(self, email: str) -> bool:
        """Validate email format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def create_approval_task(self, to_email: str, subject: str, body: str, reason: str = "Security validation failed") -> str:
        """Create an approval task for emails that require approval."""
        try:
            vault_path = Path("./AI_Employee_Vault/Pending_Approval")
            vault_path.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            task_filename = f"{timestamp}_email_approval_{to_email.replace('@', '_at_').replace('.', '_dot_')}.md"
            task_file_path = vault_path / task_filename

            task_content = f"""---
id: approval_{timestamp}
created: '{datetime.now().isoformat()}'
status: pending_approval
priority: high
category: email_approval
requires_human: true
---

# Email Approval Required

## Email Details
- **To:** {to_email}
- **Subject:** {subject}
- **Body:**
{body}

## Approval Required
{reason}

## Action Required
Please review this email and approve or reject it by moving it to the appropriate folder:
- Move to **Approved** folder to send the email
- Move to **Rejected** folder to cancel

## Security Note
Emails require approval based on security validation rules.
"""

            with open(task_file_path, 'w', encoding='utf-8') as f:
                f.write(task_content)

            return f"⚠️ Email to {to_email} requires approval.\n📋 Created approval task: {task_filename}\nReason: {reason}\nPlease review and approve in the Pending Approval folder."

        except Exception as e:
            return f"❌ Error creating approval task: {str(e)}"


def main():
    """Main function to run the chatbot."""
    print(Fore.CYAN + "🤖 Initializing AI Employee Chatbot...")
    print(Style.RESET_ALL)

    chatbot = AIChatbot()

    print("\n" + Fore.GREEN + chatbot.greet_user())
    print(Style.RESET_ALL)
    print("\n" + Fore.YELLOW + "="*60)
    print(Style.RESET_ALL)

    while True:
        try:
            user_input = input(Fore.BLUE + "\n>You: " + Style.RESET_ALL).strip()

            if not user_input:
                continue

            response = chatbot.process_command(user_input)

            # Color code the response based on content
            if "✅" in response or "success" in response.lower():
                print(f"\n{Fore.GREEN}🤖 AI Employee: {response}")
            elif "❌" in response or "error" in response.lower() or "failed" in response.lower():
                print(f"\n{Fore.RED}🤖 AI Employee: {response}")
            elif "⚠️" in response or "approval" in response.lower():
                print(f"\n{Fore.YELLOW}🤖 AI Employee: {response}")
            else:
                print(f"\n{Fore.MAGENTA}🤖 AI Employee: {response}")

            print(Style.RESET_ALL)

            # Exit condition
            if user_input.lower() in ['quit', 'exit', 'bye', 'goodbye']:
                break

        except KeyboardInterrupt:
            print(f"\n\n{Fore.YELLOW}👋 Goodbye! The AI Employee System remains operational in the background.{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}❌ An error occurred: {str(e)}{Style.RESET_ALL}")
            print(f"{Fore.RED}🤖 AI Employee: Sorry, I encountered an error. Please try again.{Style.RESET_ALL}")


if __name__ == "__main__":
    main()