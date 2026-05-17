"""
Notification Service
Handles sending notifications, alerts, and building notification messages.

PERFORMANCE ISSUE: This module uses inefficient string concatenation in loops
instead of more efficient methods like f-strings or str.join().
"""

import time
from datetime import datetime
from typing import List, Dict


class NotificationService:
    """Service for managing and sending notifications."""
    
    def __init__(self):
        self.notification_queue = []
        self.sent_notifications = []
        
    def build_user_activity_report(self, user_activities: List[Dict]) -> str:
        """
        Build a detailed activity report for a user.
        
        PERFORMANCE ISSUE: Uses inefficient string concatenation in a loop.
        For large datasets, this creates many intermediate string objects,
        causing poor performance and high memory usage.
        
        SUGGESTION: Use f-strings or str.join() for better performance.
        """
        # INEFFICIENT: String concatenation in loop
        report = ""
        report = report + "=" * 50 + "\n"
        report = report + "USER ACTIVITY REPORT\n"
        report = report + "=" * 50 + "\n"
        report = report + f"Generated at: {datetime.now().isoformat()}\n"
        report = report + f"Total activities: {len(user_activities)}\n"
        report = report + "-" * 50 + "\n\n"
        
        # VERY INEFFICIENT: Concatenating in a loop
        for idx, activity in enumerate(user_activities, 1):
            report = report + f"Activity #{idx}\n"
            report = report + f"  Type: {activity.get('type', 'N/A')}\n"
            report = report + f"  Timestamp: {activity.get('timestamp', 'N/A')}\n"
            report = report + f"  User: {activity.get('user_id', 'N/A')}\n"
            report = report + f"  Details: {activity.get('details', 'N/A')}\n"
            report = report + f"  Status: {activity.get('status', 'N/A')}\n"
            report = report + "-" * 30 + "\n"
        
        report = report + "\n" + "=" * 50 + "\n"
        report = report + "END OF REPORT\n"
        report = report + "=" * 50 + "\n"
        
        return report
    
    def generate_transaction_log(self, transactions: List[Dict]) -> str:
        """
        Generate a formatted log of transactions.
        
        PERFORMANCE ISSUE: Another example of inefficient string building.
        """
        # INEFFICIENT: Building string with += operator in loop
        log_message = ""
        log_message += "TRANSACTION LOG\n"
        log_message += "=" * 60 + "\n"
        
        total_amount = 0
        
        # INEFFICIENT: Multiple concatenations per iteration
        for transaction in transactions:
            log_message += f"\nTransaction ID: {transaction.get('id', 'N/A')}\n"
            log_message += f"Date: {transaction.get('date', 'N/A')}\n"
            log_message += f"Amount: ${transaction.get('amount', 0):.2f}\n"
            log_message += f"Type: {transaction.get('type', 'N/A')}\n"
            log_message += f"Status: {transaction.get('status', 'N/A')}\n"
            log_message += f"Description: {transaction.get('description', 'N/A')}\n"
            log_message += "-" * 60 + "\n"
            
            total_amount += transaction.get('amount', 0)
        
        log_message += f"\nTotal Amount: ${total_amount:.2f}\n"
        log_message += "=" * 60 + "\n"
        
        return log_message
    
    def create_email_notification(self, recipient: str, subject: str, 
                                  data: Dict) -> str:
        """
        Create an email notification body.
        
        PERFORMANCE ISSUE: Inefficient string concatenation for email body.
        """
        # INEFFICIENT: Building email body with concatenation
        email_body = ""
        email_body = email_body + "Dear User,\n\n"
        email_body = email_body + f"Subject: {subject}\n\n"
        email_body = email_body + "This is an automated notification from our system.\n\n"
        
        # INEFFICIENT: Concatenating data fields
        email_body = email_body + "Details:\n"
        email_body = email_body + "-" * 40 + "\n"
        
        for key, value in data.items():
            email_body = email_body + f"{key}: {value}\n"
        
        email_body = email_body + "-" * 40 + "\n\n"
        email_body = email_body + "If you have any questions, please contact support.\n\n"
        email_body = email_body + "Best regards,\n"
        email_body = email_body + "The System Team\n"
        
        return email_body
    
    def build_error_summary(self, errors: List[Dict]) -> str:
        """
        Build a summary of system errors.
        
        PERFORMANCE ISSUE: Yet another inefficient string building pattern.
        """
        # INEFFICIENT: String concatenation in loop
        summary = ""
        summary += "ERROR SUMMARY REPORT\n"
        summary += "=" * 70 + "\n"
        summary += f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        summary += f"Total errors: {len(errors)}\n"
        summary += "=" * 70 + "\n\n"
        
        # Group errors by severity
        critical_count = 0
        warning_count = 0
        info_count = 0
        
        # INEFFICIENT: Multiple string operations in loop
        for error in errors:
            severity = error.get('severity', 'unknown').upper()
            
            summary += f"[{severity}] "
            summary += f"{error.get('timestamp', 'N/A')} - "
            summary += f"{error.get('message', 'No message')}\n"
            summary += f"  Module: {error.get('module', 'N/A')}\n"
            summary += f"  Code: {error.get('error_code', 'N/A')}\n"
            
            if error.get('stack_trace'):
                summary += f"  Stack trace:\n"
                # VERY INEFFICIENT: Nested concatenation
                for line in error['stack_trace'].split('\n'):
                    summary += f"    {line}\n"
            
            summary += "\n"
            
            # Count by severity
            if severity == 'CRITICAL':
                critical_count += 1
            elif severity == 'WARNING':
                warning_count += 1
            else:
                info_count += 1
        
        # INEFFICIENT: More concatenation for summary
        summary += "=" * 70 + "\n"
        summary += "SUMMARY BY SEVERITY\n"
        summary += "-" * 70 + "\n"
        summary += f"Critical: {critical_count}\n"
        summary += f"Warning: {warning_count}\n"
        summary += f"Info: {info_count}\n"
        summary += "=" * 70 + "\n"
        
        return summary
    
    def format_notification_batch(self, notifications: List[Dict]) -> str:
        """
        Format a batch of notifications for display or logging.
        
        PERFORMANCE ISSUE: Inefficient string building for batch processing.
        """
        # INEFFICIENT: Building large string with concatenation
        batch_output = ""
        batch_output = batch_output + "\n" + "=" * 80 + "\n"
        batch_output = batch_output + "NOTIFICATION BATCH\n"
        batch_output = batch_output + "=" * 80 + "\n"
        
        # INEFFICIENT: Loop with multiple concatenations
        for i, notification in enumerate(notifications, 1):
            batch_output = batch_output + f"\n[{i}/{len(notifications)}] "
            batch_output = batch_output + f"ID: {notification.get('id', 'N/A')}\n"
            batch_output = batch_output + f"Type: {notification.get('type', 'N/A')}\n"
            batch_output = batch_output + f"Priority: {notification.get('priority', 'normal')}\n"
            batch_output = batch_output + f"Recipient: {notification.get('recipient', 'N/A')}\n"
            batch_output = batch_output + f"Message: {notification.get('message', 'N/A')}\n"
            batch_output = batch_output + f"Created: {notification.get('created_at', 'N/A')}\n"
            batch_output = batch_output + "-" * 80 + "\n"
        
        batch_output = batch_output + "\n" + "=" * 80 + "\n"
        batch_output = batch_output + f"Total notifications in batch: {len(notifications)}\n"
        batch_output = batch_output + "=" * 80 + "\n"
        
        return batch_output
    
    def send_notification(self, notification_type: str, recipient: str, 
                         message: str) -> bool:
        """
        Send a notification to a recipient.
        
        This method is fine - it doesn't have string concatenation issues.
        """
        notification = {
            'id': f"notif_{int(time.time())}",
            'type': notification_type,
            'recipient': recipient,
            'message': message,
            'created_at': datetime.now().isoformat(),
            'status': 'sent'
        }
        
        self.sent_notifications.append(notification)
        return True


# Module-level helper function with inefficient string building
def build_system_status_message(components: List[Dict]) -> str:
    """
    Build a system status message.
    
    PERFORMANCE ISSUE: Inefficient string concatenation pattern.
    """
    # INEFFICIENT: String concatenation
    status_msg = ""
    status_msg = status_msg + "SYSTEM STATUS\n"
    status_msg = status_msg + "=" * 50 + "\n"
    
    for component in components:
        status_msg = status_msg + f"\n{component['name']}:\n"
        status_msg = status_msg + f"  Status: {component['status']}\n"
        status_msg = status_msg + f"  Uptime: {component['uptime']}\n"
        status_msg = status_msg + f"  Load: {component['load']}\n"
    
    status_msg = status_msg + "\n" + "=" * 50 + "\n"
    
    return status_msg

# Made with Bob
