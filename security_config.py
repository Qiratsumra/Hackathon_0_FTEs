"""
Security Configuration for AI Employee System

Defines approval thresholds, permission boundaries, and safety rules
for the AI Employee system.

Author: AI Employee System
Created: 2026-01-22
"""

import os
from typing import Dict, List, Tuple, Any
from enum import Enum
from dataclasses import dataclass
from pathlib import Path
import logging


class ApprovalLevel(Enum):
    """Enumeration of approval levels."""
    AUTO_APPROVE = "auto_approve"
    MANUAL_APPROVE = "manual_approve"
    HUMAN_REQUIRED = "human_required"


class ActionType(Enum):
    """Enumeration of action types that require security checks."""
    EMAIL = "email"
    PAYMENT = "payment"
    FILE_ACCESS = "file_access"
    SYSTEM_CONFIG = "system_config"
    DATA_ACCESS = "data_access"
    COMMUNICATION = "communication"


@dataclass
class SecurityRule:
    """Definition of a security rule."""
    action_type: ActionType
    description: str
    approval_level: ApprovalLevel
    threshold_value: float = 0.0
    conditions: List[str] = None
    exceptions: List[str] = None

    def __post_init__(self):
        if self.conditions is None:
            self.conditions = []
        if self.exceptions is None:
            self.exceptions = []


class SecurityConfig:
    """Security configuration manager for the AI Employee system."""

    def __init__(self, vault_path: str = "~/AI_Employee_Vault"):
        self.vault_path = Path(vault_path).expanduser()
        self.logger = logging.getLogger('security_config')

        # Load configuration from environment or defaults
        self.approval_threshold_low = float(os.getenv('APPROVAL_THRESHOLD_LOW', '50'))
        self.approval_threshold_high = float(os.getenv('APPROVAL_THRESHOLD_HIGH', '100'))
        self.monthly_revenue_target = float(os.getenv('MONTHLY_REVENUE_TARGET', '4000'))

        # Define security rules
        self.rules = self._define_security_rules()

        # Known contacts (loaded from contacts file or environment)
        self.known_contacts = self._load_known_contacts()

        # Sensitive operations
        self.sensitive_operations = {
            'delete_files': True,
            'modify_system_settings': True,
            'access_financial_data': True,
            'share_private_info': True,
            'terminate_services': True
        }

        self.logger.info("Security configuration initialized")

    def _define_security_rules(self) -> List[SecurityRule]:
        """Define the security rules for the system."""
        return [
            # Email rules
            SecurityRule(
                action_type=ActionType.EMAIL,
                description="Email replies to known contacts",
                approval_level=ApprovalLevel.AUTO_APPROVE,
                conditions=["contact_known"],
                exceptions=[]
            ),
            SecurityRule(
                action_type=ActionType.EMAIL,
                description="Emails to unknown contacts",
                approval_level=ApprovalLevel.MANUAL_APPROVE,
                conditions=["contact_unknown"],
                exceptions=[]
            ),
            SecurityRule(
                action_type=ActionType.EMAIL,
                description="Emails containing payment information",
                approval_level=ApprovalLevel.MANUAL_APPROVE,
                conditions=["contains_payment_terms"],
                exceptions=[]
            ),
            SecurityRule(
                action_type=ActionType.EMAIL,
                description="Social media interactions",
                approval_level=ApprovalLevel.MANUAL_APPROVE,
                conditions=["social_media_context"],
                exceptions=["scheduled_posts_approved"]
            ),

            # Payment rules
            SecurityRule(
                action_type=ActionType.PAYMENT,
                description="Recurring payments under threshold",
                approval_level=ApprovalLevel.AUTO_APPROVE,
                threshold_value=self.approval_threshold_low,
                conditions=["recurring", "amount_less_than_threshold"],
                exceptions=["whitelisted_vendors"]
            ),
            SecurityRule(
                action_type=ActionType.PAYMENT,
                description="Payments between thresholds",
                approval_level=ApprovalLevel.MANUAL_APPROVE,
                threshold_value=self.approval_threshold_high,
                conditions=["amount_between_thresholds"],
                exceptions=[]
            ),
            SecurityRule(
                action_type=ActionType.PAYMENT,
                description="Payments over high threshold",
                approval_level=ApprovalLevel.HUMAN_REQUIRED,
                threshold_value=self.approval_threshold_high,
                conditions=["amount_greater_than_threshold"],
                exceptions=[]
            ),
            SecurityRule(
                action_type=ActionType.PAYMENT,
                description="Payments to new payees",
                approval_level=ApprovalLevel.MANUAL_APPROVE,
                conditions=["new_payee"],
                exceptions=[]
            ),

            # File access rules
            SecurityRule(
                action_type=ActionType.FILE_ACCESS,
                description="File organization and archiving",
                approval_level=ApprovalLevel.AUTO_APPROVE,
                conditions=["archival_operation"],
                exceptions=[]
            ),
            SecurityRule(
                action_type=ActionType.FILE_ACCESS,
                description="File deletion operations",
                approval_level=ApprovalLevel.MANUAL_APPROVE,
                conditions=["deletion_operation"],
                exceptions=["temporary_files"]
            ),

            # System configuration rules
            SecurityRule(
                action_type=ActionType.SYSTEM_CONFIG,
                description="System configuration changes",
                approval_level=ApprovalLevel.HUMAN_REQUIRED,
                conditions=["config_change"],
                exceptions=[]
            ),

            # Data access rules
            SecurityRule(
                action_type=ActionType.DATA_ACCESS,
                description="Access to sensitive financial data",
                approval_level=ApprovalLevel.MANUAL_APPROVE,
                conditions=["access_sensitive_data"],
                exceptions=["reporting_purposes"]
            ),
            SecurityRule(
                action_type=ActionType.DATA_ACCESS,
                description="Sharing of private information",
                approval_level=ApprovalLevel.HUMAN_REQUIRED,
                conditions=["share_private_info"],
                exceptions=[]
            )
        ]

    def _load_known_contacts(self) -> List[str]:
        """Load known contacts from configuration."""
        # In a real implementation, this would load from a contacts file or database
        # For now, we'll use environment variables or defaults
        contacts_env = os.getenv('KNOWN_CONTACTS', '')
        if contacts_env:
            return [email.strip() for email in contacts_env.split(',') if email.strip()]

        # Default known contacts (would come from user's actual contact list)
        return [
            'bysaeed110@gmail.com',
            'your-business-email@company.com',
            'admin@yourbusiness.com'
        ]

    def check_approval_needed(self, action_type: ActionType, **kwargs) -> Tuple[ApprovalLevel, str]:
        """
        Check if an action requires approval based on security rules.

        Args:
            action_type: Type of action being performed
            **kwargs: Additional context for the action

        Returns:
            Tuple of (ApprovalLevel, reason for the decision)
        """
        # Find applicable rules
        applicable_rules = [rule for rule in self.rules if rule.action_type == action_type]

        for rule in applicable_rules:
            # Check if conditions are met
            conditions_met = self._check_conditions(rule, kwargs)

            if conditions_met and not self._check_exceptions(rule, kwargs):
                return rule.approval_level, rule.description

        # Default to manual approval if no specific rule matches
        return ApprovalLevel.MANUAL_APPROVE, "No specific rule matched, defaulting to manual approval"

    def _check_conditions(self, rule: SecurityRule, context: Dict[str, Any]) -> bool:
        """Check if the conditions for a rule are met."""
        if not rule.conditions:
            return True  # No conditions means rule always applies

        # For simplicity, we'll check if any condition is present in context
        # In a real implementation, this would be more sophisticated
        for condition in rule.conditions:
            if condition in context:
                if isinstance(context[condition], bool):
                    if context[condition]:
                        return True
                else:
                    return True

        # Special handling for threshold conditions
        if 'amount' in context and rule.threshold_value > 0:
            amount = float(context['amount'])

            if condition == "amount_less_than_threshold":
                return amount < rule.threshold_value
            elif condition == "amount_between_thresholds":
                return rule.approval_threshold_low <= amount <= rule.approval_threshold_high
            elif condition == "amount_greater_than_threshold":
                return amount > rule.threshold_value

        return False

    def _check_exceptions(self, rule: SecurityRule, context: Dict[str, Any]) -> bool:
        """Check if any exceptions apply to prevent the rule from triggering."""
        for exception in rule.exceptions:
            if exception in context:
                if isinstance(context[exception], bool):
                    if context[exception]:
                        return True
                else:
                    return True
        return False

    def is_known_contact(self, contact_identifier: str) -> bool:
        """
        Check if a contact is known.

        Args:
            contact_identifier: Email address or other identifier

        Returns:
            True if contact is known, False otherwise
        """
        # Normalize the contact identifier
        normalized_contact = contact_identifier.lower().strip()

        # Check against known contacts
        for known_contact in self.known_contacts:
            if normalized_contact == known_contact.lower().strip():
                return True

        # Check if it's a domain match for known business contacts
        for known_contact in self.known_contacts:
            if '@' in known_contact and '@' in normalized_contact:
                known_domain = known_contact.split('@')[1]
                contact_domain = normalized_contact.split('@')[1]
                if known_domain == contact_domain:
                    return True

        return False

    def validate_payment_request(self, amount: float, recipient: str, description: str = "") -> Tuple[bool, str]:
        """
        Validate a payment request against security rules.

        Args:
            amount: Payment amount
            recipient: Payment recipient
            description: Description of payment purpose

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check amount thresholds
        if amount > self.approval_threshold_high:
            return False, f"Payment amount ${amount} exceeds high threshold of ${self.approval_threshold_high}. Requires human approval."

        if amount > self.approval_threshold_low:
            return False, f"Payment amount ${amount} exceeds low threshold of ${self.approval_threshold_low}. Requires manual approval."

        # Check if recipient is new (not in known contacts)
        if not self.is_known_contact(recipient):
            return False, f"Payment to new recipient '{recipient}'. Requires approval."

        # Check for suspicious keywords in description
        suspicious_keywords = ['urgent', 'immediate', 'wire transfer', 'gift card', 'bitcoin', 'cash']
        if description:
            for keyword in suspicious_keywords:
                if keyword.lower() in description.lower():
                    return False, f"Suspicious keyword '{keyword}' found in payment description. Requires approval."

        return True, "Payment request validated successfully."

    def validate_email_request(self, recipient: str, subject: str, content: str) -> Tuple[bool, str]:
        """
        Validate an email request against security rules.

        Args:
            recipient: Email recipient
            subject: Email subject
            content: Email content

        Returns:
            Tuple of (is_valid, reason)
        """
        # Check if recipient is known
        if not self.is_known_contact(recipient):
            return False, f"Email to unknown contact '{recipient}'. Requires approval."

        # Check for sensitive information in content
        sensitive_keywords = ['password', 'credit card', 'ssn', 'social security', 'bank account', 'api key']
        for keyword in sensitive_keywords:
            if keyword.lower() in content.lower():
                return False, f"Sensitive information '{keyword}' detected in email content. Requires approval."

        # Check for suspicious links
        import re
        link_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        links = re.findall(link_pattern, content)
        if links and not self.is_known_contact(recipient):
            return False, f"Email to unknown contact contains {len(links)} external links. Requires approval."

        return True, "Email request validated successfully."

    def validate_file_operation(self, operation_type: str, file_path: str, **kwargs) -> Tuple[bool, str]:
        """
        Validate a file operation against security rules.

        Args:
            operation_type: Type of operation (read, write, delete, etc.)
            file_path: Path of the file being operated on
            **kwargs: Additional context

        Returns:
            Tuple of (is_valid, reason)
        """
        file_path_obj = Path(file_path)

        # Check if trying to delete files
        if operation_type.lower() == 'delete':
            # Never auto-approve file deletion
            return False, "File deletion operations require approval."

        # Check if accessing sensitive files
        sensitive_patterns = ['.env', '.pem', '.key', 'secrets', 'credentials', 'config']
        for pattern in sensitive_patterns:
            if pattern.lower() in file_path_obj.name.lower():
                return False, f"Access to potentially sensitive file '{file_path}'. Requires approval."

        # Check if modifying system files
        system_file_patterns = ['mcp.json', 'security_config.py', 'orchestrator.py', 'base_watcher.py']
        if file_path_obj.name in system_file_patterns:
            return False, f"Modification of system file '{file_path}'. Requires human approval."

        return True, "File operation validated successfully."

    def get_approval_thresholds(self) -> Dict[str, float]:
        """Get the current approval thresholds."""
        return {
            'low': self.approval_threshold_low,
            'high': self.approval_threshold_high,
            'monthly_revenue_target': self.monthly_revenue_target
        }

    def update_thresholds(self, low: float = None, high: float = None, revenue_target: float = None):
        """
        Update approval thresholds.

        Args:
            low: New low threshold
            high: New high threshold
            revenue_target: New revenue target
        """
        if low is not None:
            self.approval_threshold_low = float(low)
            os.environ['APPROVAL_THRESHOLD_LOW'] = str(low)

        if high is not None:
            self.approval_threshold_high = float(high)
            os.environ['APPROVAL_THRESHOLD_HIGH'] = str(high)

        if revenue_target is not None:
            self.monthly_revenue_target = float(revenue_target)
            os.environ['MONTHLY_REVENUE_TARGET'] = str(revenue_target)

        self.logger.info(f"Updated thresholds - Low: ${self.approval_threshold_low}, High: ${self.approval_threshold_high}")

    def log_security_event(self, event_type: str, action: str, result: str, details: str = ""):
        """
        Log a security-related event.

        Args:
            event_type: Type of security event
            action: Action that triggered the event
            result: Result of the security check
            details: Additional details about the event
        """
        self.logger.info(f"SECURITY EVENT: {event_type} - {action} - {result} - {details}")


# Global security configuration instance
security_config = SecurityConfig()


def check_approval_needed(action_type: ActionType, **kwargs) -> Tuple[ApprovalLevel, str]:
    """
    Convenience function to check if an action needs approval.

    Args:
        action_type: Type of action being performed
        **kwargs: Additional context for the action

    Returns:
        Tuple of (ApprovalLevel, reason for the decision)
    """
    return security_config.check_approval_needed(action_type, **kwargs)


def validate_payment(amount: float, recipient: str, description: str = "") -> Tuple[bool, str]:
    """
    Convenience function to validate a payment request.

    Args:
        amount: Payment amount
        recipient: Payment recipient
        description: Description of payment purpose

    Returns:
        Tuple of (is_valid, reason)
    """
    return security_config.validate_payment_request(amount, recipient, description)


def validate_email(recipient: str, subject: str, content: str) -> Tuple[bool, str]:
    """
    Convenience function to validate an email request.

    Args:
        recipient: Email recipient
        subject: Email subject
        content: Email content

    Returns:
        Tuple of (is_valid, reason)
    """
    return security_config.validate_email_request(recipient, subject, content)


def validate_file_operation(operation_type: str, file_path: str, **kwargs) -> Tuple[bool, str]:
    """
    Convenience function to validate a file operation.

    Args:
        operation_type: Type of operation (read, write, delete, etc.)
        file_path: Path of the file being operated on
        **kwargs: Additional context

    Returns:
        Tuple of (is_valid, reason)
    """
    return security_config.validate_file_operation(operation_type, file_path, **kwargs)


if __name__ == "__main__":
    # Example usage
    print("Security Configuration Loaded")
    print(f"Approval Thresholds: Low=${security_config.approval_threshold_low}, High=${security_config.approval_threshold_high}")
    print(f"Known Contacts: {len(security_config.known_contacts)}")

    # Example validation
    is_valid, reason = validate_payment(75.0, "vendor@example.com", "Monthly subscription")
    print(f"Payment validation: {is_valid}, Reason: {reason}")

    is_valid, reason = validate_email("client@known.com", "Project Update", "Here's the latest project status...")
    print(f"Email validation: {is_valid}, Reason: {reason}")