# AI Employee System Documentation

Welcome to the documentation for the AI Employee System - an autonomous business automation platform that uses AI to manage emails, messages, tasks, and business operations 24/7.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Components](#components)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)
9. [API Reference](#api-reference)
10. [FAQ](#faq)

## Overview

The AI Employee System is designed to act as an autonomous employee that can handle routine business operations while maintaining proper oversight and approval workflows. The system integrates with Obsidian as a knowledge base, Claude Code as a reasoning engine, and various Python scripts for monitoring and automation.

### Key Features

- **Automated Task Processing**: Converts emails and files into structured tasks
- **Intelligent Routing**: Routes tasks based on type and priority
- **Approval Workflow**: Multi-tier approval system for sensitive actions
- **Web Dashboard**: Real-time monitoring and management interface
- **Email Integration**: Gmail API integration for automated email processing
- **File Monitoring**: Continuous monitoring of dropzone for new files
- **Reporting**: Daily and weekly briefing generation
- **Security**: Comprehensive security and approval system

## Architecture

The system follows a component-based architecture with clear separation of concerns:

### Component Architecture

1. **Input Layer**:
   - File Watcher: Monitors dropzone folder for new files
   - Gmail Watcher: Monitors Gmail account for new/important emails
   - Base Watcher: Abstract base class for all watchers

2. **Processing Layer**:
   - Orchestrator: Master coordinator managing all system components
   - Task Processing Engine: Processes tasks from Needs_Action folder
   - Skills Layer: Defines how AI handles different types of tasks

3. **Action Layer**:
   - MCP Servers: Handle various actions (email, file, payment, browser)
   - Security Configuration: Enforces approval requirements

4. **Data Layer**:
   - Obsidian Vault: File-based storage system
   - Configuration files: System settings and business rules

## Installation

See the [SETUP_GUIDE.md](../SETUP_GUIDE.md) for detailed installation instructions.

## Configuration

Configuration is managed through environment variables and the `security_config.py` file. See [Configuration Guide](configuration.md) for details.

## Usage

### Starting the System

```bash
python orchestrator.py
```

### Monitoring

Access the web dashboard at `http://localhost:8000` to monitor system status.

## Components

Detailed component documentation:

- [Orchestrator](components/orchestrator.md)
- [Watchers](components/watchers.md)
- [MCP Servers](components/mcp-servers.md)
- [Skills Framework](components/skills.md)
- [Dashboard](components/dashboard.md)

## Security

The system implements a multi-layered security approach:

- **Approval System**: Three-tier system (auto-approve, manual approve, human required)
- **Contact Validation**: Known vs. unknown contact handling
- **Threshold Management**: Payment and action limits
- **Validation Layers**: Multiple checks for email, payment, and file operations
- **Audit Logging**: Complete action history

## Troubleshooting

Common issues and solutions are documented in the [TROUBLESHOOTING.md](../TROUBLESHOOTING.md) file.

## API Reference

For developers looking to extend the system, see the [API Reference](api-reference.md).

## FAQ

Frequently asked questions about the system:

**Q: How does the approval system work?**
A: The system uses a three-tier approval system based on transaction amounts and risk factors. See the security documentation for details.

**Q: Can I customize the skills?**
A: Yes, the skills framework is designed to be extensible. See the skills documentation for details.

**Q: How do I monitor system health?**
A: Use the web dashboard at http://localhost:8000 or check the log files in the Logs directory.