"""
Admin Notification Service for Critical Alerts
Handles sending notifications to administrators when critical failures occur
"""

import os
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Optional, Dict
import requests
import json
from pathlib import Path


class AdminNotificationService:
    """Service for sending critical alerts to administrators"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Email configuration
        self.smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('SMTP_PORT', '587'))
        self.smtp_username = os.getenv('SMTP_USERNAME')
        self.smtp_password = os.getenv('SMTP_PASSWORD')
        self.admin_emails = os.getenv('ADMIN_EMAILS', '').split(',')
        
        # Webhook configuration (for Slack, Discord, etc.)
        self.webhook_url = os.getenv('ADMIN_WEBHOOK_URL')
        
        # Telegram configuration
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_ADMIN_CHAT_ID')
        
        # Alert log file
        self.alert_log_file = Path('logs/critical_alerts.log')
        self.alert_log_file.parent.mkdir(exist_ok=True)
        
        # Rate limiting to prevent spam
        self.alert_cache = {}
        self.rate_limit_minutes = 30  # Don't send same alert more than once per 30 minutes
    
    def send_critical_alert(
        self, 
        subject: str, 
        message: str, 
        service: str,
        priority: str = 'HIGH',
        additional_data: Optional[Dict] = None
    ) -> bool:
        """
        Send critical alert through all configured channels
        
        Args:
            subject: Alert subject
            message: Alert message
            service: Service that triggered the alert
            priority: Alert priority (LOW, MEDIUM, HIGH, CRITICAL)
            additional_data: Additional context data
            
        Returns:
            bool: True if at least one notification was sent successfully
        """
        
        # Check rate limiting
        cache_key = f"{service}:{subject}"
        if self._is_rate_limited(cache_key):
            self.logger.info(f"Alert rate limited: {cache_key}")
            return False
        
        # Log the alert
        self._log_alert(subject, message, service, priority)
        
        success = False
        
        # Try all configured notification channels
        try:
            # Email notification
            if self.smtp_username and self.smtp_password and self.admin_emails:
                if self._send_email_alert(subject, message, service, priority):
                    success = True
        except Exception as e:
            self.logger.error(f"Email notification failed: {str(e)}")
        
        try:
            # Webhook notification (Slack, Discord, etc.)
            if self.webhook_url:
                if self._send_webhook_alert(subject, message, service, priority):
                    success = True
        except Exception as e:
            self.logger.error(f"Webhook notification failed: {str(e)}")
        
        try:
            # Telegram notification
            if self.telegram_bot_token and self.telegram_chat_id:
                if self._send_telegram_alert(subject, message, service, priority):
                    success = True
        except Exception as e:
            self.logger.error(f"Telegram notification failed: {str(e)}")
        
        # Update rate limit cache
        if success:
            self._update_rate_limit_cache(cache_key)
        
        return success
    
    def _send_email_alert(
        self, 
        subject: str, 
        message: str, 
        service: str, 
        priority: str
    ) -> bool:
        """Send email alert to administrators"""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"[{priority}] Kuwait Social AI Alert: {subject}"
            msg['From'] = self.smtp_username
            msg['To'] = ', '.join(self.admin_emails)
            
            # Create HTML content
            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: {'#d32f2f' if priority == 'CRITICAL' else '#f57c00'};">
                    {priority} Alert: {subject}
                </h2>
                
                <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
                    <p><strong>Service:</strong> {service}</p>
                    <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC</p>
                </div>
                
                <div style="margin-top: 20px;">
                    <h3>Alert Details:</h3>
                    <pre style="background-color: #eeeeee; padding: 10px; border-radius: 5px;">
{message}
                    </pre>
                </div>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    This is an automated alert from Kuwait Social AI platform.
                    Please investigate and take appropriate action.
                </p>
            </body>
            </html>
            """
            
            # Attach parts
            text_part = MIMEText(message, 'plain')
            html_part = MIMEText(html_content, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)
            
            self.logger.info(f"Email alert sent successfully: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email alert: {str(e)}")
            return False
    
    def _send_webhook_alert(
        self, 
        subject: str, 
        message: str, 
        service: str, 
        priority: str
    ) -> bool:
        """Send webhook alert (compatible with Slack, Discord, etc.)"""
        try:
            # Slack-compatible format
            payload = {
                "text": f"*{priority} Alert:* {subject}",
                "blocks": [
                    {
                        "type": "header",
                        "text": {
                            "type": "plain_text",
                            "text": f"{priority} Alert: {subject}"
                        }
                    },
                    {
                        "type": "section",
                        "fields": [
                            {"type": "mrkdwn", "text": f"*Service:*\n{service}"},
                            {"type": "mrkdwn", "text": f"*Time:*\n{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"}
                        ]
                    },
                    {
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": f"*Details:*\n```{message}```"
                        }
                    }
                ],
                "attachments": [
                    {
                        "color": "#d32f2f" if priority == "CRITICAL" else "#f57c00",
                        "fallback": message
                    }
                ]
            }
            
            response = requests.post(
                self.webhook_url,
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            response.raise_for_status()
            
            self.logger.info(f"Webhook alert sent successfully: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send webhook alert: {str(e)}")
            return False
    
    def _send_telegram_alert(
        self, 
        subject: str, 
        message: str, 
        service: str, 
        priority: str
    ) -> bool:
        """Send Telegram alert"""
        try:
            # Format message for Telegram
            emoji = "🚨" if priority == "CRITICAL" else "⚠️"
            telegram_message = f"""
{emoji} *{priority} ALERT*

*Subject:* {subject}
*Service:* {service}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

*Details:*
```
{message}
```
            """
            
            # Send to Telegram
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            payload = {
                'chat_id': self.telegram_chat_id,
                'text': telegram_message,
                'parse_mode': 'Markdown'
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            self.logger.info(f"Telegram alert sent successfully: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram alert: {str(e)}")
            return False
    
    def _log_alert(
        self, 
        subject: str, 
        message: str, 
        service: str, 
        priority: str
    ):
        """Log alert to file for audit trail"""
        try:
            with open(self.alert_log_file, 'a') as f:
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'priority': priority,
                    'service': service,
                    'subject': subject,
                    'message': message
                }
                f.write(json.dumps(log_entry) + '\n')
        except Exception as e:
            self.logger.error(f"Failed to log alert: {str(e)}")
    
    def _is_rate_limited(self, cache_key: str) -> bool:
        """Check if alert is rate limited"""
        if cache_key in self.alert_cache:
            last_sent = self.alert_cache[cache_key]
            time_since = (datetime.now() - last_sent).total_seconds() / 60
            return time_since < self.rate_limit_minutes
        return False
    
    def _update_rate_limit_cache(self, cache_key: str):
        """Update rate limit cache"""
        self.alert_cache[cache_key] = datetime.now()
        
        # Clean old entries
        cutoff_time = datetime.now()
        self.alert_cache = {
            k: v for k, v in self.alert_cache.items()
            if (cutoff_time - v).total_seconds() / 60 < self.rate_limit_minutes * 2
        }
    
    def test_notifications(self) -> Dict[str, bool]:
        """Test all notification channels"""
        results = {}
        
        test_message = f"""
This is a test notification from Kuwait Social AI platform.
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC

If you receive this message, the notification channel is working correctly.
        """
        
        # Test each channel
        if self.smtp_username and self.admin_emails:
            results['email'] = self._send_email_alert(
                "Test Notification",
                test_message,
                "AdminNotificationService",
                "LOW"
            )
        
        if self.webhook_url:
            results['webhook'] = self._send_webhook_alert(
                "Test Notification",
                test_message,
                "AdminNotificationService",
                "LOW"
            )
        
        if self.telegram_bot_token and self.telegram_chat_id:
            results['telegram'] = self._send_telegram_alert(
                "Test Notification",
                test_message,
                "AdminNotificationService",
                "LOW"
            )
        
        return results


# Singleton instance
_notification_service = None


def get_notification_service() -> AdminNotificationService:
    """Get singleton notification service instance"""
    global _notification_service
    if _notification_service is None:
        _notification_service = AdminNotificationService()
    return _notification_service


# Convenience function
def send_critical_alert(
    subject: str, 
    message: str, 
    service: str,
    priority: str = 'HIGH',
    additional_data: Optional[Dict] = None
) -> bool:
    """Send critical alert through notification service"""
    return get_notification_service().send_critical_alert(
        subject=subject,
        message=message,
        service=service,
        priority=priority,
        additional_data=additional_data
    )