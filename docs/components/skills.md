# Skills Framework

The Skills Framework provides domain-specific knowledge and instructions for the AI Employee.

## Overview

Skills define how the AI Employee should handle different types of tasks and operations. They provide context-specific instructions, templates, and guidelines.

## Core Skills

### Email Responder
Handles email responses with appropriate tone and templates.

**Key Features:**
- Professional but friendly communication
- Different templates for known vs. unknown contacts
- Priority classification
- Approval triggers
- Follow-up protocols

### Task Processor
Analyzes incoming tasks and creates detailed action plans.

**Key Features:**
- Task classification and prioritization
- Information extraction
- Plan creation with steps and timelines
- Risk assessment
- Success validation

### Approval Creator
Manages the approval workflow for sensitive operations.

**Key Features:**
- Automatic approval determination
- Escalation protocols
- Human approval requests
- Threshold management
- Compliance checking

### Log Writer
Maintains consistent logging and documentation.

**Key Features:**
- Standardized log format
- Activity tracking
- Error logging
- Audit trail maintenance
- Performance metrics

### Briefing Generator
Creates executive briefings and reports.

**Key Features:**
- Daily status briefings
- Weekly CEO briefings
- KPI tracking
- Trend analysis
- Recommendation generation

## Skill Structure

Skills are defined as Markdown files in the `.claude/skills/` directory with the following structure:

1. **Purpose**: Description of the skill's function
2. **Core Principles**: Fundamental guidelines
3. **Guidelines**: Detailed instructions for operation
4. **Templates**: Standard formats and responses
5. **Special Scenarios**: Handling edge cases
6. **Quality Metrics**: Success measurement criteria

## Integration

Skills are automatically loaded and used by Claude Code when processing tasks. The system selects appropriate skills based on:

- Task content and type
- Current system state
- Security requirements
- User preferences