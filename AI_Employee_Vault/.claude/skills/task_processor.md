# 📋 Task Processor Skill

## Purpose
Analyze incoming tasks and create detailed action plans. This skill enables the AI Employee to understand task requirements, prioritize appropriately, and generate executable plans for task completion.

## Task Analysis Framework

### 1. Task Classification
- **Type**: Email response, File processing, Data entry, Payment processing, Meeting prep, Research, Report generation, etc.
- **Priority**: Urgent (immediate), High (same day), Medium (2-3 days), Low (week)
- **Complexity**: Simple (under 30 mins), Moderate (30 mins-2 hours), Complex (2+ hours)
- **Resource Needs**: Internal knowledge only, External research, Human approval, Third-party integration

### 2. Information Extraction
- **Action Required**: What specifically needs to be done
- **Context**: Background information and constraints
- **Deadline**: When task needs completion
- **Dependencies**: Other tasks or information needed first
- **Success Criteria**: How to know task is completed successfully

## Processing Workflow

### Step 1: Initial Assessment
1. Read the entire task document
2. Identify the core request
3. Determine urgency and importance
4. Check against Company_Handbook.md for guidelines
5. Identify if approval is required

### Step 2: Information Gathering
1. Collect all relevant context
2. Identify missing information
3. Determine required resources
4. Check for conflicts with other tasks
5. Verify data accuracy

### Step 3: Plan Creation
1. Break task into specific, actionable steps
2. Estimate time for each step
3. Identify potential obstacles
4. Plan for contingencies
5. Define success metrics

## Plan Structure

### Standard Plan Template
```markdown
# Task Plan: [Task Title]

## Overview
- **Objective**: [Clear statement of what needs to be accomplished]
- **Priority**: [Urgent/High/Medium/Low]
- **Estimated Duration**: [Time estimate]
- **Success Criteria**: [How to measure completion]

## Prerequisites
- [ ] [Any requirements before starting]
- [ ] [Access needed]
- [ ] [Information needed]

## Action Steps
1. **[Step 1]** - [Description]
   - Expected outcome: [Result]
   - Time estimate: [Duration]
   - Dependencies: [Any prerequisites]

2. **[Step 2]** - [Description]
   - Expected outcome: [Result]
   - Time estimate: [Duration]
   - Dependencies: [Any prerequisites]

[Continue for all steps]

## Resources Needed
- [List of tools, information, or access required]

## Potential Risks
- [Risk 1]: [Mitigation strategy]
- [Risk 2]: [Mitigation strategy]

## Success Validation
- [ ] [How to verify step 1 completion]
- [ ] [How to verify step 2 completion]
- [ ] [Overall task completion criteria]
```

## Priority Determination

### High Priority (Do First)
- Tasks with approaching deadlines
- Revenue-generating activities
- Customer service issues
- Urgent emails requiring response
- Tasks flagged as high priority by human

### Medium Priority (Schedule)
- Routine business operations
- Administrative tasks
- Follow-up activities
- Research and preparation

### Low Priority (Batch Process)
- Long-term projects
- Information gathering
- System maintenance
- Non-urgent correspondence

## Decision Points

### Does This Need Approval?
- **YES** if: Payment involved over $50, new vendor/client, legal matters, sensitive information
- **NO** if: Routine email response, file organization, internal task management, scheduled posts

### What Type of Task Is This?
- **Communication**: Email responses, messages, notifications
- **Processing**: Data entry, file management, invoice processing
- **Research**: Information gathering, market analysis, competitive intelligence
- **Planning**: Schedule coordination, meeting prep, strategic planning
- **Execution**: Task completion, payment processing, delivery arrangements

## Quality Assurance

### Before Finalizing Plan
- [ ] All steps are specific and actionable
- [ ] Timeline is realistic
- [ ] Resources are available
- [ ] Risks are identified and mitigated
- [ ] Success criteria are measurable
- [ ] Approval requirements are identified

### During Execution Checkpoints
- [ ] Progress against timeline
- [ ] Resource availability
- [ ] Quality of intermediate results
- [ ] Need for plan adjustment

## Common Task Patterns

### Email Response Task
1. Analyze sender and context
2. Determine appropriate response template
3. Customize message for recipient
4. Check for approval requirements
5. Schedule or send

### File Processing Task
1. Identify file type and purpose
2. Determine appropriate action (organize, convert, analyze)
3. Apply business rules for categorization
4. Move to appropriate location
5. Create follow-up tasks if needed

### Data Entry Task
1. Validate data format and completeness
2. Map to appropriate fields/systems
3. Enter data following standards
4. Verify accuracy
5. Update tracking systems

### Research Task
1. Define specific information needed
2. Identify reliable sources
3. Gather and organize information
4. Analyze and summarize findings
5. Present in requested format

## Escalation Guidelines

### When to Escalate
- Unclear instructions or requirements
- Conflicts with other priorities
- Missing critical information
- Approaching deadline with insufficient resources
- Ethical or legal concerns
- Technology limitations preventing completion

### Escalation Format
```
TASK ESCALATION

Task: [Task name and ID]
Issue: [Describe the problem preventing completion]
Impact: [Effect on business operations]
Options: [Possible solutions]
Recommendation: [Preferred solution]
Action Needed: [Specific help requested]
```

## Integration Points

### With Other Skills
- Coordinate with email_responder for communication tasks
- Use approval_creator for tasks requiring authorization
- Update log_writer with progress and outcomes
- Feed information to briefing_generator for reporting

### With System Components
- Update dashboard status indicators
- Create/update task tracking files
- Maintain logs in appropriate format
- Trigger notifications when needed