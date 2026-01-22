# 🏗️ AI Employee System Architecture

Detailed documentation of the system architecture and component interactions.

## 📐 System Overview

The AI Employee system is an autonomous business automation platform consisting of several interconnected components:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Input Layer   │────│ Processing Layer │────│  Action Layer   │
│                 │    │                  │    │                 │
│ • File Dropzone │    │ • Orchestrator   │    │ • MCP Servers   │
│ • Gmail         │    │ • Claude Code    │    │ • Email MCP     │
│ • Other Inputs  │    │ • Task Manager   │    │ • File MCP      │
└─────────────────┘    │ • Skills Engine  │    │ • Payment MCP   │
                       └──────────────────┘    └─────────────────┘
                                │
                       ┌──────────────────┐
                       │   Data Layer     │
                       │                  │
                       │ • Obsidian Vault │
                       │ • Task Storage   │
                       │ • Logs           │
                       │ • Config Files   │
                       └──────────────────┘
```

## 🏗️ Component Architecture

### 1. Input Layer

#### File Watcher (`file_watcher.py`)
- **Purpose**: Monitors a designated dropzone folder for new files
- **Function**: Creates markdown task files in `Needs_Action/` when new files are detected
- **Features**:
  - Duplicate detection using file hashing
  - Supported file types filtering
  - Proper error handling and recovery
  - Configurable polling intervals

#### Gmail Watcher (`gmail_watcher.py`)
- **Purpose**: Monitors Gmail account for new/important emails
- **Function**: Creates task files from important emails
- **Features**:
  - OAuth2 authentication with Gmail API
  - Configurable email filters
  - Email content parsing and decoding
  - Duplicate detection using email IDs

#### Base Watcher (`base_watcher.py`)
- **Purpose**: Abstract base class for all watchers
- **Function**: Provides common functionality for monitoring and task creation
- **Features**:
  - Standardized logging
  - Error recovery with exponential backoff
  - YAML frontmatter metadata handling
  - Markdown task file generation

### 2. Processing Layer

#### Orchestrator (`orchestrator.py`)
- **Purpose**: Master coordinator that manages all system components
- **Functions**:
  - Monitors vault folders for changes
  - Coordinates task processing workflows
  - Manages watcher processes
  - Performs health checks
  - Generates reports and briefings
  - Handles scheduled tasks

**Key Features**:
- File system monitoring with watchdog
- Process management for watchers
- Task queuing and scheduling
- Health monitoring and reporting
- Daily/weekly briefing generation
- Graceful startup/shutdown handling

#### Task Processing Engine
- **Purpose**: Processes tasks from `Needs_Action/` folder
- **Function**: Analyzes tasks and creates action plans
- **Components**:
  - Task classifier and analyzer
  - Plan generator
  - Approval request creator
  - Status updater

### 3. Skills Layer

Located in `AI_Employee_Vault/.claude/skills/`, these define how the AI should handle different types of tasks:

#### Email Responder (`email_responder.md`)
- **Purpose**: Guidelines for drafting professional email responses
- **Function**: Defines response templates and approval requirements
- **Features**:
  - Known vs. unknown contact handling
  - Response templates and tone guidelines
  - Approval triggers and escalation procedures

#### Task Processor (`task_processor.md`)
- **Purpose**: Framework for analyzing and creating plans for tasks
- **Function**: Defines task analysis methodology
- **Features**:
  - Task classification system
  - Plan structure templates
  - Priority determination
  - Quality assurance protocols

#### Approval Creator (`approval_creator.md`)
- **Purpose**: Standardized process for creating approval requests
- **Function**: Defines when and how to request human approval
- **Features**:
  - Approval categories and thresholds
  - Request templates
  - Tracking and follow-up procedures

#### Log Writer (`log_writer.md`)
- **Purpose**: Standardized logging practices
- **Function**: Defines how to maintain activity logs
- **Features**:
  - Log structure and format
  - Event categorization
  - Performance monitoring
  - Security logging

#### Briefing Generator (`briefing_generator.md`)
- **Purpose**: Framework for generating CEO briefings
- **Function**: Defines briefing structure and content
- **Features**:
  - Weekly and daily briefing templates
  - Data collection and analysis
  - Performance metrics
  - Recommendation generation

### 4. Data Layer

#### Obsidian Vault Structure
```
AI_Employee_Vault/
├── Needs_Action/          # Incoming tasks to process
├── Plans/                 # Generated work plans
├── In_Progress/           # Currently working on
├── Pending_Approval/      # Awaiting human approval
├── Approved/              # Approved by human, ready to execute
├── Rejected/              # Rejected actions
├── Done/                  # Completed tasks (archive)
├── Logs/                  # Activity logs
├── Inbox/                 # File storage
├── Accounting/            # Financial records
├── Briefings/             # Weekly CEO briefings
└── .claude/
    └── skills/            # Agent skills folder
```

#### Core Documentation Files
- **Dashboard.md**: Real-time status overview
- **Company_Handbook.md**: Business rules and preferences
- **Business_Goals.md**: Revenue targets and metrics

### 5. Action Layer

#### MCP Configuration (`mcp.json`)
- **Purpose**: Defines Machine Connected Protocol servers
- **Function**: Configures action execution capabilities
- **Components**:
  - Filesystem MCP: Built-in file operations
  - Email MCP: Gmail API integration
  - Browser MCP: Web interaction capabilities
  - Payment MCP: Financial transaction handling

#### Security Configuration (`security_config.py`)
- **Purpose**: Defines approval thresholds and permission boundaries
- **Function**: Enforces security policies and approval requirements
- **Features**:
  - Dynamic approval thresholds
  - Contact validation
  - Payment and email validation
  - File operation security

## 🔗 Component Interactions

### Task Flow
```
Input Detected → New File in Needs_Action → Orchestrator Detects → Claude Processes →
Plan Created → Approval Check → Action Executed → Status Updated → Log Recorded
```

### Data Flow
```
Raw Input → Watcher → Task File → Orchestrator → Skills → Action → Vault Update → Logs
```

### Control Flow
```
User Config → Orchestrator → Watchers → MCP Servers → Actions → Feedback → Status Update
```

## 🔒 Security Architecture

### Approval System
- **Auto-approve**: Known contacts, routine operations under threshold
- **Manual approve**: New contacts, operations between thresholds
- **Human required**: High-value operations, legal matters

### Validation Layers
1. **Input Validation**: Contact and content validation
2. **Business Logic**: Rule-based approval requirements
3. **Security Checks**: Fraud and risk assessment
4. **Logging**: Complete audit trail

### Access Control
- **Environment variables**: Sensitive configuration
- **File permissions**: Vault access controls
- **API scopes**: Minimal required permissions
- **Network restrictions**: Whitelisted domains only

## 📊 Monitoring and Observability

### Health Checks
- **Component status**: Watcher and service availability
- **Performance metrics**: Response times and throughput
- **Resource usage**: Memory, CPU, disk space
- **Error tracking**: Failure detection and recovery

### Logging Strategy
- **Application logs**: Component-specific operational logs
- **Security logs**: Access and approval events
- **Performance logs**: Response times and resource usage
- **Audit trails**: Complete action history

## 🚀 Scalability Considerations

### Current Architecture
- **Single-instance**: Designed for individual use
- **File-based**: Relies on local file system
- **Sequential processing**: Tasks processed one at a time

### Future Extensions
- **Queue system**: For handling high-volume scenarios
- **Database backend**: For improved querying and analysis
- **Distributed workers**: For parallel task processing
- **Cloud deployment**: For remote operation

## 🔄 Integration Points

### External APIs
- **Google APIs**: Gmail, Calendar, Drive
- **Payment processors**: Stripe, PayPal, bank APIs
- **Web services**: Social media, CRM, ERP systems

### Internal Interfaces
- **File system**: Vault folder monitoring
- **CLI tools**: Command-line interfaces
- **API endpoints**: Future REST API possibilities

This architecture enables the AI Employee system to operate autonomously while maintaining security, accountability, and traceability for all business operations.