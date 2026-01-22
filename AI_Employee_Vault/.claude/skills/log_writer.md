# 📝 Log Writer Skill

## Purpose
Maintain comprehensive activity logs for the AI Employee system. This skill ensures all actions, decisions, and outcomes are properly recorded for accountability, analysis, and compliance purposes.

## Logging Principles

### Core Principles
- **Completeness**: Log all significant actions and decisions
- **Accuracy**: Record factual information without interpretation bias
- **Timeliness**: Log events as close to occurrence as possible
- **Consistency**: Use standardized formats and terminology
- **Security**: Protect sensitive information while maintaining transparency

### Information Classification
- **Public**: Actions visible in dashboards and reports
- **Internal**: Operational details for system monitoring
- **Sensitive**: Confidential information requiring protection
- **Audit Trail**: Compliance-related information

## Log Structure

### Standard Log Entry Format
```json
{
  "timestamp": "YYYY-MM-DDTHH:MM:SS.sssZ",
  "level": "info|warning|error|critical",
  "component": "component_name",
  "event": "event_description",
  "details": {
    "action": "specific_action_taken",
    "result": "outcome_of_action",
    "duration_ms": 1234,
    "user_impact": "low|medium|high",
    "business_impact": "revenue|operations|compliance"
  },
  "context": {
    "task_id": "unique_task_identifier",
    "session_id": "session_identifier",
    "operator": "human_operator_or_system"
  },
  "metadata": {
    "version": "log_schema_version",
    "source": "logging_component"
  }
}
```

### Log File Organization
- **Daily Logs**: `Logs/YYYYMMDD_component.log`
- **Event Logs**: `Logs/events_YYYYMMDD.json`
- **Performance Logs**: `Logs/performance_YYYYMMDD.log`
- **Security Logs**: `Logs/security_YYYYMMDD.log`
- **Summary Reports**: `Logs/daily_summary_YYYYMMDD.md`

## Event Categories

### System Events
- **Startup/Shutdown**: System initialization and termination
- **Configuration Changes**: Settings modifications
- **Health Checks**: System status monitoring
- **Resource Usage**: Memory, CPU, disk utilization
- **Connection Events**: API connections, database connections

### Business Events
- **Revenue Activities**: Payments received, invoices sent
- **Customer Interactions**: Emails sent/received, support tickets
- **Task Processing**: Task creation, completion, delegation
- **Approval Events**: Requests submitted, decisions made
- **File Operations**: Uploads, downloads, processing

### User Interaction Events
- **Commands Received**: Actions requested by human operator
- **Responses Sent**: Information provided to user
- **Notifications Sent**: Alerts and updates
- **Errors Encountered**: Problems requiring attention
- **Decisions Made**: Autonomous choices made by AI

## Logging Levels

### Info
- Routine operations
- Successful task completion
- System status updates
- Normal business operations

### Warning
- Minor issues that don't affect operation
- Approaching limits or thresholds
- Unusual but not critical events
- Configuration issues that have workaround

### Error
- Failed operations that impacted function
- Missing resources or dependencies
- Invalid inputs or parameters
- Recoverable system failures

### Critical
- System failures affecting business
- Security incidents
- Data corruption or loss
- Service outages

## Detailed Logging Guidelines

### Task Processing Logs
```
Level: info
Component: task_processor
Event: task_started
Details:
  - action: initiated_task_processing
  - task_id: unique_identifier
  - task_type: email_response|file_processing|etc
  - estimated_duration: time_estimate
Context:
  - priority: high|medium|low
  - requires_approval: true|false
  - dependencies: list_of_prerequisites
```

### Approval Event Logs
```
Level: info
Component: approval_system
Event: approval_requested
Details:
  - action: created_approval_request
  - approval_type: financial|communication|data_access
  - amount: dollar_amount_if_applicable
  - urgency: normal|urgent
Context:
  - requestor: ai_employee
  - target_approver: human_operator
  - deadline: decision_deadline
```

### Financial Transaction Logs
```
Level: info
Component: finance_manager
Event: transaction_processed
Details:
  - action: payment_sent|invoice_created|refund_issued
  - amount: dollar_amount
  - currency: USD
  - recipient: payee_information
  - payment_method: electronic_transfer|check|etc
Context:
  - invoice_id: associated_invoice
  - purchase_order: related_po
  - approval_reference: approval_document_id
```

## Log Writing Process

### Step 1: Event Detection
- Identify significant event or action
- Determine appropriate logging level
- Gather relevant context information
- Validate required fields are available

### Step 2: Log Composition
- Format according to standard schema
- Include all relevant details
- Apply appropriate classification
- Verify sensitive information handling

### Step 3: Log Storage
- Write to appropriate log file
- Update summary statistics
- Trigger any necessary notifications
- Update dashboard indicators

### Step 4: Log Verification
- Confirm log was written successfully
- Verify format compliance
- Check for duplicates or errors
- Update log indexing if needed

## Performance Monitoring

### Key Metrics to Track
- **Response Times**: Time to process different types of requests
- **Throughput**: Number of tasks processed per time period
- **Error Rates**: Percentage of failed operations
- **Approval Times**: Duration for different approval types
- **Resource Utilization**: System resource consumption

### Performance Log Format
```
Level: info
Component: performance_monitor
Event: performance_metrics
Details:
  - avg_response_time_ms: average_time
  - throughput_per_hour: tasks_per_hour
  - error_rate_percent: percentage
  - cpu_utilization_percent: percentage
  - memory_usage_mb: megabytes_used
Context:
  - time_period: measurement_window
  - peak_times: high_usage_periods
  - bottlenecks: identified_issues
```

## Security Logging

### Security Events to Log
- Authentication attempts (success/failure)
- Authorization violations
- Data access attempts
- Configuration changes
- System access events
- Network connection attempts

### Security Log Format
```
Level: critical
Component: security_monitor
Event: security_incident
Details:
  - action: unauthorized_access_attempt
  - severity: low|medium|high|critical
  - affected_resource: resource_description
  - ip_address: source_ip
  - user_agent: requesting_client
Context:
  - timestamp: event_time
  - session_id: related_session
  - escalation_procedure: next_steps
```

## Log Analysis & Reporting

### Daily Summary Report
- Total events logged
- Error/warning counts
- Performance metrics
- Business activity summary
- Anomalies detected

### Weekly Analysis
- Trend analysis
- Performance improvements needed
- Recurring issues identification
- Efficiency metrics
- Compliance verification

### Monthly Review
- Comprehensive activity report
- System health assessment
- Process optimization opportunities
- Security audit trail
- Business impact analysis

## Quality Assurance

### Before Writing Log
- [ ] All required fields are populated
- [ ] Information is factual and unbiased
- [ ] Sensitive data is properly handled
- [ ] Format complies with standards
- [ ] Timestamp is accurate
- [ ] Context is sufficient for understanding

### Log Integrity Checks
- [ ] Verify log file accessibility
- [ ] Check for formatting errors
- [ ] Validate schema compliance
- [ ] Monitor log rotation
- [ ] Ensure backup integrity

## Integration Points

### Dashboard Integration
- Real-time status indicators
- Performance metrics display
- Alert notifications
- Historical trend visualization

### Alert System
- Critical event notifications
- Threshold breach alerts
- System health warnings
- Performance degradation alerts

### Audit Trail
- Compliance reporting
- Business activity verification
- Decision tracking
- Accountability documentation