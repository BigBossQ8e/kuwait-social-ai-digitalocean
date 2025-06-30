"""
Email utility functions for Kuwait Social AI
"""

from flask import current_app
from flask_mail import Message, Mail
import logging

logger = logging.getLogger(__name__)

# Initialize Flask-Mail (will be configured in app factory)
mail = Mail()


def send_welcome_email(user_email, user_name=None):
    """
    Send a welcome email to newly registered users
    
    Args:
        user_email (str): The recipient's email address
        user_name (str, optional): The user's name for personalization
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        subject = "Welcome to Kuwait Social AI!"
        
        # Prepare the email body
        if user_name:
            body = f"""
Hello {user_name},

Welcome to Kuwait Social AI! We're excited to have you on board.

Your account has been successfully created. You can now log in and start exploring our AI-powered social media management platform.

Here's what you can do with Kuwait Social AI:
- Generate engaging content for your social media channels
- Schedule posts across multiple platforms
- Analyze your social media performance
- Track competitor activities
- And much more!

If you have any questions or need assistance, please don't hesitate to reach out to our support team.

Best regards,
The Kuwait Social AI Team
"""
        else:
            body = """
Hello,

Welcome to Kuwait Social AI! We're excited to have you on board.

Your account has been successfully created. You can now log in and start exploring our AI-powered social media management platform.

Here's what you can do with Kuwait Social AI:
- Generate engaging content for your social media channels
- Schedule posts across multiple platforms
- Analyze your social media performance
- Track competitor activities
- And much more!

If you have any questions or need assistance, please don't hesitate to reach out to our support team.

Best regards,
The Kuwait Social AI Team
"""
        
        # Create the message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@kuwaitsocial.ai')
        )
        
        # Send the email
        mail.send(msg)
        logger.info(f"Welcome email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user_email}: {str(e)}")
        return False


def send_password_reset_email(user_email, reset_token):
    """
    Send a password reset email
    
    Args:
        user_email (str): The recipient's email address
        reset_token (str): The password reset token
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        subject = "Password Reset Request - Kuwait Social AI"
        
        # Get the frontend URL from config
        frontend_url = current_app.config.get('FRONTEND_URL', 'https://kwtsocial.com')
        reset_url = f"{frontend_url}/reset-password?token={reset_token}"
        
        body = f"""
Hello,

We received a request to reset your password for your Kuwait Social AI account.

To reset your password, please click the link below:
{reset_url}

This link will expire in 1 hour for security reasons.

If you didn't request this password reset, please ignore this email. Your password will remain unchanged.

Best regards,
The Kuwait Social AI Team
"""
        
        # Create the message
        msg = Message(
            subject=subject,
            recipients=[user_email],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@kuwaitsocial.ai')
        )
        
        # Send the email
        mail.send(msg)
        logger.info(f"Password reset email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send password reset email to {user_email}: {str(e)}")
        return False


def send_notification_email(user_email, subject, body):
    """
    Send a general notification email
    
    Args:
        user_email (str): The recipient's email address
        subject (str): Email subject
        body (str): Email body
    
    Returns:
        bool: True if email was sent successfully, False otherwise
    """
    try:
        # Create the message
        msg = Message(
            subject=f"Kuwait Social AI - {subject}",
            recipients=[user_email],
            body=body,
            sender=current_app.config.get('MAIL_DEFAULT_SENDER', 'noreply@kuwaitsocial.ai')
        )
        
        # Send the email
        mail.send(msg)
        logger.info(f"Notification email sent successfully to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification email to {user_email}: {str(e)}")
        return False