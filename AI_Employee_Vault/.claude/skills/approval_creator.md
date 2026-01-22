# 🗳️ Approval Creator Skill

## Purpose
Create standardized approval requests for sensitive actions that require human oversight. This skill ensures proper authorization before executing potentially risky operations.

## Approval Categories

### Financial Approvals
- **Low Risk** ($1-$49): Auto-approve based on rules
- **Medium Risk** ($50-$100): Standard approval request
- **High Risk** ($100+): Detailed justification required
- **Exceptional** (Unlimited): Full business case needed

### Communication Approvals
- **Known Contacts**: Auto-approve routine communications
- **New Contacts**: Approval for first-time outreach
- **Sensitive Topics**: Approval for legal/financial discussions
- **Marketing Content**: Approval for public-facing content

### Data & Access Approvals
- **Internal Data**: Standard access based on need
- **External Sharing**: Approval for sharing business data
- **System Access**: Authorization for new integrations
- **Privacy**: Approval for personal information handling

## Approval Request Structure

### Standard Approval Template
```markdown
---
status: pending_approval
priority: high
category: [financial/data/communication/other]
created: [timestamp]
expires: [time when decision needed]
estimated_value: [dollar amount if applicable]
---

# 📋 ACTION REQUIRES APPROVAL

## Summary
**Action**: [Brief description of what needs approval]
**Value/Potential Impact**: [Financial impact or significance]
**Urgency**: [Timeline for decision needed]

## Detailed Description
[Full description of the action that needs approval, including context and reason]

## Options
1. **Approve**: [Action will proceed as planned]
2. **Modify**: [Suggest alternative approach]
3. **Reject**: [Action will be cancelled]
4. **Defer**: [Decision postponed]

## Justification
- [Reason 1 for the proposed action]
- [Reason 2 for the proposed action]
- [Expected benefits]

## Risk Assessment
- **Low Risk**: [Description of minimal risks]
- **Medium Risk**: [Description of moderate risks]
- **High Risk**: [Description of significant risks]

## Recommended Action
[Clear recommendation with reasoning]

## Next Steps if Approved
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Additional Information
[Links to related documents, context, or supporting materials]

---
**Submitted by**: AI Employee System
**Submitted at**: [Timestamp]
**Decision Required by**: [Deadline]
**Contact**: [How to reach AI if questions arise]
---
```

## Trigger Conditions

### Automatic Approval Creation
- Payment requests over $50
- Communications with unknown contacts
- File deletions
- System configuration changes
- Access requests for sensitive data
- Contract or agreement discussions
- Social media posting (non-scheduled)
- Vendor onboarding
- Subscription changes

### Context Requirements
- **Financial**: Amount, recipient, purpose, payment method
- **Communication**: Recipient, topic, sensitivity level, business relationship
- **Data**: Type of data, destination, purpose, recipients
- **System**: Change type, impact assessment, rollback plan

## Approval Workflow

### Step 1: Detection
- Identify action that requires approval
- Gather all relevant context
- Determine approval level needed

### Step 2: Documentation
- Create comprehensive approval request
- Include all necessary context
- Format according to template

### Step 3: Submission
- Place in Pending_Approval folder
- Update dashboard status
- Log creation event
- Notify human operator if urgent

### Step 4: Tracking
- Monitor approval status
- Follow up if needed
- Handle approved/rejected outcomes appropriately

## Risk Levels & Documentation

### Level 1: Basic Approval
- **Threshold**: $50-$100 or moderate risk
- **Documentation**: Standard template
- **Information needed**: Basic justification
- **Timeline**: 24 hours

### Level 2: Enhanced Approval
- **Threshold**: $100-$500 or high risk
- **Documentation**: Detailed business case
- **Information needed**: ROI projections, alternatives considered
- **Timeline**: 48 hours

### Level 3: Executive Approval
- **Threshold**: $500+ or exceptional risk
- **Documentation**: Full business proposal
- **Information needed**: Strategic alignment, risk mitigation
- **Timeline**: 1 week

## Conditional Approvals

### Situational Triggers
- **Emergency**: Faster approval process for urgent matters
- **Pattern Recognition**: Streamlined approval for repeated actions
- **Budget Availability**: Approval based on current budget status
- **Seasonal Factors**: Different thresholds during peak seasons

## Approval Response Handling

### If Approved
- Execute the approved action
- Log the completion
- Update status in system
- Send confirmation notification

### If Rejected
- Cancel the proposed action
- Log the rejection reason
- Update task status
- Suggest alternatives if appropriate

### If Modified
- Implement the modified approach
- Log the changes
- Proceed with updated plan

### If Deferred
- Pause the action
- Set reminder for follow-up
- Monitor changing conditions
- Re-submit when appropriate

## Escalation Procedures

### For Missing Approvals
- Follow up after 24 hours
- Escalate after 72 hours
- Consider alternatives after 1 week
- Document delays for process improvement

### For Urgent Approvals
- Mark as urgent in request
- Send notification to human operator
- Provide expedited information
- Offer temporary solutions if safe

## Quality Checks

### Before Submitting Approval Request
- [ ] All required information is included
- [ ] Risk assessment is complete
- [ ] Alternative options are considered
- [ ] Timeline is realistic
- [ ] Business justification is clear
- [ ] Compliance requirements are met

### Approval Request Review
- [ ] Clear summary of action needed
- [ ] Appropriate detail level
- [ ] Balanced presentation of pros/cons
- [ ] Clear decision options
- [ ] Proper urgency classification

## Integration with Other Systems

### Dashboard Updates
- Update pending approval count
- Highlight urgent requests
- Track approval times
- Monitor approval patterns

### Logging Integration
- Record approval request creation
- Track decision outcomes
- Monitor approval effectiveness
- Analyze approval patterns

### Notification System
- Alert human operator for urgent requests
- Remind for pending approvals
- Confirm receipt of decisions
- Report approval statistics