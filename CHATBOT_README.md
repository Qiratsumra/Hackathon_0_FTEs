# AI Employee Chatbot

The AI Employee Chatbot provides a conversational interface for controlling and interacting with the AI Employee System.

## Overview

The chatbot allows you to:
- 📧 Send emails through the system
- 📋 Manage tasks and workflows
- 📊 Check system status and statistics
- 🔍 Find information in the knowledge base
- 📝 Create new tasks or notes
- 📈 Generate reports and briefings

## Getting Started

### Prerequisites
- Python 3.13+
- All dependencies from `requirements.txt`

### Installation
```bash
pip install -r requirements.txt
```

### Running the Chatbot
```bash
python start_chatbot.py
```

Or directly:
```bash
python ai_employee_chatbot.py
```

## Available Commands

### Email Operations
- `send email to [email] subject [subject] body [message]` - Send an email
- `check email [optional: sender/filter]` - Check recent emails

### Task Management
- `create task [task description]` - Create a new task
- `list tasks` - Show current tasks in different folders
- `create task process file [filename]` - Create a file processing task

### System Operations
- `status` - Check system status
- `generate report daily` - Generate daily briefing
- `generate report weekly` - Generate weekly briefing

### Information
- `search [keyword]` - Search in the knowledge base
- `find [term]` - Find information in vault

### General
- `help` - Show help menu
- `quit` - Exit the chatbot

## Examples

### Send an Email
```
send email to john@example.com subject Hello body Hi John, how are you?
```

### Create a Task
```
create task Process the quarterly reports and prepare summary
```

### Check System Status
```
status
```

### Search for Information
```
search quarterly reports
```

## Security Features

- Unknown contacts require approval before sending emails
- All email communications are logged
- Task approval workflows are enforced
- System access is monitored

## Integration

The chatbot integrates with:
- Email MCP server for sending/receiving emails
- File system MCP for managing tasks
- Claude integration for intelligent processing
- Security configuration for approval workflows

## Troubleshooting

### Common Issues
1. **Email sending fails**: Check that your `.env` file has the correct email credentials
2. **Commands not recognized**: Type `help` to see all available commands
3. **System status shows errors**: Check the log files in `AI_Employee_Vault/Logs/`

### Environment Variables
Make sure you have the required environment variables set in your `.env` file:
```
CLAUDE_API_KEY=your_claude_api_key
GMAIL_CLIENT_ID=your_gmail_client_id
GMAIL_CLIENT_SECRET=your_gmail_client_secret
GMAIL_REFRESH_TOKEN=your_gmail_refresh_token
GMAIL_USER_EMAIL=your_email@gmail.com
```

## Support

For support, check the main system documentation or create an issue in the repository.